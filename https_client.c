#include <stdio.h> /* printf, sprintf */
#include <stdlib.h> /* exit, atoi, malloc, free */
#include <unistd.h> /* read, write, close */
#include <string.h> /* memcpy, memset */
#include <resolv.h>
#include "openssl/ssl.h"
#include "openssl/err.h"
#include <sys/types.h>
#include <sys/socket.h> /* socket, connect */
#include <netdb.h> /* struct hostent, gethostbyname */
#include <netinet/in.h> /* struct sockaddr_in, struct sockaddr */
#include <arpa/inet.h>
#include <time.h>
#include <zlib.h>

#define FAIL    -1

int opt;
int count = 0;
/*---------------------------------------------------------------------*/
/*--- error - displays errors and exits.                            ---*/
/*---------------------------------------------------------------------*/
void error(const char * msg)
{
	perror(msg); 
	exit(0);
}

/*---------------------------------------------------------------------*/
/*--- delay - delays program by specified seconds.                  ---*/
/*---------------------------------------------------------------------*/
void delay( float seconds )
{   // Pretty crossplatform, both ALL POSIX compliant systems AND Windows
    #ifdef _WIN32
        Sleep( (int) (1000 * seconds) );
    #else
        usleep( (useconds_t)(1000000 * seconds) );
    #endif
}

/*---------------------------------------------------------------------*/
/*--- OpenConnection - create socket and connect to server.         ---*/
/*---------------------------------------------------------------------*/
int OpenConnection(const char *hostname, int port)
{   int sd;
	struct sockaddr_in addr;
	struct hostent *host;

	sd = socket(AF_INET, SOCK_STREAM, 0);
	if (sd < 0) 
	{
		error("ERROR opening socket");   
	}

	bzero(&addr, sizeof(addr));
	/*if ( (inet_pton(AF_INET,hostname,&addr.sin_addr)) == -1 )
	{
		fprintf(stderr,"ERROR converting IP\n");
		exit(0);
	}*/
	host = gethostbyname(hostname);
    if (host == NULL)
    {
        fprintf(stderr,"ERROR, no such host\n");
        exit(0);
    }

	addr.sin_family = AF_INET;
	addr.sin_port = htons(port);
	bcopy((char *)host->h_addr, 
		 (char *)&addr.sin_addr.s_addr,
		 host->h_length);
	//addr.sin_addr.s_addr = *(long*)(host->h_addr);
	if ( connect(sd, (struct sockaddr*)&addr, sizeof(struct sockaddr)) != 0 )
	{
		error("ERROR connecting");
	}
	return sd;
}

/*---------------------------------------------------------------------*/
/*--- InitCTX - initialize the SSL engine.                          ---*/
/*---------------------------------------------------------------------*/
SSL_CTX* InitCTX(void)
{   
	const SSL_METHOD *method;
	SSL_CTX *ctx;

	(void)SSL_library_init();
	//init_openssl_library();
	OpenSSL_add_all_algorithms();		/* Load cryptos, et.al. */
	OpenSSL_add_all_ciphers();
	OpenSSL_add_all_digests();
	SSL_load_error_strings();			/* Bring in and register error messages */
	method = SSLv23_client_method();		/* Create new client-method instance */
	//printf("i am here\n");
	ctx = SSL_CTX_new(method);			/* Create new context */
	//printf("now here\n");
	if ( ctx == NULL )
	{
		ERR_print_errors_fp(stderr);
		abort();
	}
	//printf("should be here\n");
	return ctx;
}

/*---------------------------------------------------------------------*/
/*--- ShowCerts - print out the certificates.                       ---*/
/*---------------------------------------------------------------------*/
void ShowCerts(SSL* ssl)
{   X509 *cert;
	char *line;

	cert = SSL_get_peer_certificate(ssl);	/* get the server's certificate */
	if ( cert != NULL )
	{
		printf("Server certificates:\n");
		line = X509_NAME_oneline(X509_get_subject_name(cert), 0, 0);
		printf("Subject: %s\n", line);
		free(line);							/* free the malloc'ed string */
		line = X509_NAME_oneline(X509_get_issuer_name(cert), 0, 0);
		printf("Issuer: %s\n", line);
		free(line);							/* free the malloc'ed string */
		X509_free(cert);					/* free the malloc'ed certificate copy */
	}
	else
		printf("No certificates.\n");
}

/*---------------------------------------------------------------------*/
/*--- Send_Request - send the request.                              ---*/
/*---------------------------------------------------------------------*/
void Send_Request(char * message, SSL *ssl, unsigned long long int total)
{
	unsigned long long int sent,bytes;
	//printf("total = %d\n", total);
	sent = 0;
	do {
		bytes = SSL_write(ssl,message+sent,total-sent);
		if (bytes < 0)
			error("ERROR writing message to socket");
		if (bytes == 0)
			break;
		sent+=bytes;
	} while (sent < total);

}

/*---------------------------------------------------------------------*/
/*--- Receive_Response - receive the reponse.                       ---*/
/*---------------------------------------------------------------------*/
void  Receive_Response(SSL *ssl)
{
	unsigned long long int total,received,bytes;
	char response[1024000];
	char name[128];
//  printf("@@ %d\n",sizeof(response)); 
	memset(response,0,sizeof(response));
	total = sizeof(response)-1;
	received = 0;
	do {
		bytes = SSL_read(ssl,response+received,total-received);
		if (bytes < 0)
			error("ERROR reading response from socket");
		if (bytes == 0)
			break;
		received+=bytes;
	} while (received < total);

	printf("\nResponse: \n%s\n\n",response);
	
	if(opt == 11)
	{	
		sprintf(name,"response/response_%d_%d.txt" ,opt,count);
	}
	else
	{
		sprintf(name,"response/response_%d.txt",opt);
		//printf("here : %s\n",name);
	}
	FILE *rsp;
	rsp = fopen(name,"w+");
	fprintf(rsp,"%s",response);
	fclose(rsp);

	if (received == total)
		error("ERROR storing complete response from socket");
}


/*---------------------------------------------------------------------*/
/*--- main - create SSL context and connect.                        ---*/
/*---------------------------------------------------------------------*/

int main (int argc, char * argv[])
{
	SSL_CTX *ctx;
	int sockfd;
	SSL *ssl;
    char *message = malloc(1024000),*response;
//	int bytes, sent, received, total, message_size;
    int message_size,size;
    int i,cnt;
	char *hostname,*portnum;

	if ( argc < 5 )
	  {
	  printf("Error, Usage: %s <hostname> <portnum> <option> <response>\n", argv[0]);
	  exit(0);
	  }

	hostname = argv[1];
	portnum = argv[2];

	ctx = InitCTX();
	ssl = SSL_new(ctx);
	SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);

	opt = atoi(argv[3]);
		switch(opt)
		{
			case -1 :
			{	
				
				SSL_CTX_free(ctx);								/* release context */
				free(message);
				return 0;
			}
			
			case 0 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}
				//printf("All Ready..!\n");

								/*--Task--*/
				message = argv[4];
				//printf("message : \n%s",message);
				Send_Request(message,ssl,strlen(message));
				//printf("request sent\n");
				Receive_Response(ssl);

				close(sockfd);
				break;
			}

			case 1 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				
				for(i=4;i<argc;i++)
				{
					message = argv[i];
					Send_Request(message,ssl,strlen(message));
					delay(1);
				}

				//printf("Message: \n%s\n", message);
				//printf("Receiving\n");
				
				Receive_Response(ssl);

				close(sockfd);

				break;
			}

			case 2 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];
				message_size = strlen(message);

				for(i=0;i<message_size;i++)
				{
					Send_Request(message+i,ssl,1);
					delay(0.05);
				}

				Receive_Response(ssl);

				close(sockfd);

				break;
			}

			case 3 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				
				for(i=4;i<argc;i++)
				{
					message = argv[i];
					Send_Request(message,ssl,strlen(message));
				}

				Receive_Response(ssl);

				close(sockfd);
				break;
			}

			case 4 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);

				close(sockfd);
				break;
			}

			case 5 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);

				close(sockfd);
				break;
			}

			case 6 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);

				close(sockfd);
				break;
			}

			case 7 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);

				close(sockfd);
				break;
			}

			case 8 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);

				close(sockfd);
				break;
			}

			case 9 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				if(argc == 5)
				{
					message = argv[4];
					Send_Request(message,ssl,strlen(message));
				}
				else
				{
					message = argv[4];
					Send_Request(message,ssl,strlen(message));
					message = argv[5];
					for(i=0;i<strlen(message);i++)
					{
						Send_Request(message,ssl,1);
						delay(0.05);
					}
				}

				Receive_Response(ssl);

				close(sockfd);
				break;
			}

			case 10 :
			{					/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);
				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				if(argc == 5)
				{
					message = argv[4];
					Send_Request(message,ssl,strlen(message));
				}
				else
				{	
					strcpy(message,argv[4]);
					FILE *ptr_file;
	    			char buf[1000];
	    			char *data = malloc(1024000);
	    			char *temp = malloc(1024);

	    			ptr_file =fopen("dummy_files/file.txt","r");
	    			if (!ptr_file)
	        		{
	        			error("Error Opening Dummy file!");
	        		}
	    
	    			while (fgets(buf,1000, ptr_file) != NULL)
	        		{
	        			strcat(data,buf);
	        		}
					strcat(data,argv[argc-1]);
					message_size = strlen(data);
					sprintf(temp,"Content-Length: %d\r\n",message_size);
					
					strcat(message,temp);
					for(i=5;i<argc-1;i++)
					{
						strcat(message,argv[i]);
					}
					strcat(message,data);
					//fflush(stdout);
					//printf("message : \n%s\n",message);
					Send_Request(message,ssl,(unsigned long long int) strlen(message));
					fclose(ptr_file);
				}
				
				Receive_Response(ssl);
				
				close(sockfd);
				SSL_CTX_free(ctx);
				break;
			}

			case 11 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				strcpy(message,argv[4]);

				Send_Request(message,ssl,strlen(message));
				count += 1;
				Receive_Response(ssl);
				
				Send_Request(message,ssl,strlen(message));
				count += 1;
				Receive_Response(ssl);
				
				Send_Request(message,ssl,strlen(message));
				count += 1;
				Receive_Response(ssl);
				
				close(sockfd);
				break;
			}

			case 12 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				//Receive_Response(ssl);
				while(1){}
				//close(sockfd);
				break;
			}

			case 13 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				///ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				//Receive_Response(ssl);
				while(1){}
				//close(sockfd);
				break;
			}

			case 14 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);
				
				close(sockfd);
				break;
			}

			case 15 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);
				
				close(sockfd);
				break;
			}

			case 16 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				if(argc == 5)
				{
					message = argv[4];
					Send_Request(message,ssl,strlen(message));
				}
				else
				{
					strcpy(message,argv[4]);
					Send_Request(message,ssl,strlen(message));
					//strcpy(message,argv[5]);
					char * a = malloc(4096);
					char * b = malloc(4096);
					strcpy(a,argv[5]);
					uLong ucompSize = strlen(a)+1;
					uLong compSize = compressBound(ucompSize);
					//printf("everything ready\n");
					//Deflate
					if((compress((Bytef *)b, &compSize, (Bytef *)a, ucompSize)) != Z_OK)
					{
						error("Error Compressing Data!!");
					}
					memcpy(message,b,compSize);
					//printf("ready to send\n");
					//printf("message: %s\n",message);
					long sent,bytes,total;
					sent = 0;
					total = (long)(compSize);
					do {
						bytes = SSL_write(ssl,message+sent,total-sent);
						if (bytes < 0)
							error("ERROR writing message to socket");
						if (bytes == 0)
							break;
						sent+=bytes;
					} while (sent < total);
					//printf("request sent\n");
				}

				struct timeval timeout;      
			    timeout.tv_sec = 20;
			    timeout.tv_usec = 0;

			    /*if (setsockopt (sockfd, SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout,
            		    sizeof(timeout)) < 0)
			        error("setsockopt failed\n");*/

			    if (setsockopt (sockfd, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout,
			                sizeof(timeout)) < 0)
			        error("setsockopt failed\n");
				Receive_Response(ssl);
				//printf("response received\n");
				close(sockfd);
				break;
			}

			case 17 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				if(argc == 5)
				{
					message = argv[4];
					Send_Request(message,ssl,strlen(message));
				}
				else
				{	
					strcpy(message,argv[4]);
					FILE *ptr_file;
	    			char buf[10000];
	    			char *data = malloc(1024000);
	    			char *temp = malloc(1024);

	    			ptr_file =fopen("dummy_files/big_file.txt","r");
	    			if (!ptr_file)
	        		{
	        			error("Error Opening Dummy file!");
	        		}
	    
	    			while (fgets(buf,10000, ptr_file) != NULL)
	        		{
	        			strcat(data,buf);
	        		}
					strcat(data,argv[argc-1]);
					message_size = strlen(data);
					sprintf(temp,"Content-Length: %d\r\n",message_size);
					
					strcat(message,temp);
					for(i=5;i<argc-1;i++)
					{
						strcat(message,argv[i]);
					}
					//printf("message : \n%s\n",message);
					strcat(message,data);
					//fflush(stdout);
					
					Send_Request(message,ssl,(unsigned long long int) strlen(message));
					fclose(ptr_file);
				}
				
				Receive_Response(ssl);
				
				close(sockfd);
				SSL_CTX_free(ctx);
				break;
			}

			case 18 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);
				
				close(sockfd);
				break;
			}

			case 19 :
			{
								/*--Connect--*/
				//ctx = InitCTX();
				sockfd = OpenConnection(hostname, atoi(portnum));
				//ssl = SSL_new(ctx);

				SSL_set_fd(ssl,sockfd);
				//SSL_set_mode(ssl, SSL_MODE_AUTO_RETRY);
				if (SSL_connect (ssl) == FAIL)
				{
					ERR_print_errors_fp(stderr);
					exit(0);
				}

								/*--Task--*/
				message = argv[4];

				Send_Request(message,ssl,strlen(message));
				Receive_Response(ssl);
				
				close(sockfd);
				break;
			}

			
			default :
         	{
         		printf("Invalid option, Try again\n" );
         	}	

		}

		//SSL_CTX_free(ctx);								/* release context */
		//free(message);
	
}
