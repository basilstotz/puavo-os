#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>

#include <err.h>
#include <fcntl.h>

#include <linux/random.h>

#define BUFSIZE 65536
/* WARNING - this struct must match random.h's struct rand_pool_info */
typedef struct {
	int bit_count;               /* number of bits of entropy in data */
	int byte_count;              /* number of bytes of data in array */
	unsigned char buf[BUFSIZE];
} entropy_t;

int
main(void)
{
	entropy_t rpi;
	int fd, i;

	fd = open("/dev/random", O_WRONLY);
	if (fd == -1)
		err(1, "error opening /dev/random");

	rpi.bit_count = BUFSIZE * 8;
	rpi.byte_count = BUFSIZE;

	for (i = 0; i < BUFSIZE; i++)
		rpi.buf[i] = i;

	if (ioctl(fd, RNDADDENTROPY, &rpi) == -1)
		err(1, "error in ioctl RNDADDENTROPY for /dev/random");

	return 0;
}
