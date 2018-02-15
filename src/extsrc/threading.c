/* ~/dev/py/xlutil_py/extsrc/threading.c */

#include "cFTLogForPy.h"

        pthread_t       writerThread;
static  int             writerReady = false;
static  pthread_mutex_t readyLock;
static  pthread_cond_t  readyCond;

// local prototypes
static void* startWriter (void * arg);
static int writerInit(void); 

// These comments have become scattered in the reorganization of the
// code.

/////////////////////////////////////////////////////////////////////
// INTERFACE TO DISK WRITER
/////////////////////////////////////////////////////////////////////

// Buffer pages are allocated in integral multiples of LOG_BUFFER_SIZE
// bytes.  Initially we allocate two log pages and the first is ACTIVE.
// When the main thread needs to write a message it gets the mutex lock
// and copies the message to the active page, so long as it will fit;
// otherwise it marks the page in use as FULL and advances to the next
// available page, marking that page as ACTIVE, and writes the message
// into it.  In either case the offset on the page written to is updated.
//
// When the disk writer thread gets control, it gets the lock and checks
// for any full pages (checking cyclically from the page following the
// active page).  Any found are marked BEING_WRITTEN, as is the active
// page.  The next free page is marked ACTIVE_BUF.  The lock is then
// released and those pages marked BEING_WRITTEN are written to disk in
// cyclic order.  When the disk write is complete, all pages are marked
// READY and their offsets reset to zero.
//
// If a signal is received, any entries written to the disk buffer should
// be flushed to disk before passing control to any other signal handler
// code.


// static void dumpBufDesc(int n, logBufDesc_t* p) {
//     printf("BUFFER %d:\n", n);
//     printf("    offset:    %5d\n", p->offset);
//     printf("    pageBytes: %5d\n", p->pageBytes);
//     printf("    flags:     %5x\n", p->flags);
//     printf("    content:   '%s'",  p->data);
// }


/////////////////////////////////////////////////////////////////////
// DISK WRITER INITIALIZATION (runs in main thread)
/////////////////////////////////////////////////////////////////////

/**
 * XXX INCORRECT DESCRIPTION:
 *
 * Start a background thread.  This opens a named log file in append mode.
 * If the log file and/or its containing directory do not exist, it or
 * they are created.  From the main thread we then allow callers to
 * write strings to a buffer.  Periodically this gets flushed to disk;
 * the write to disk occurs in the second thread.  The close() function
 * runs in the main thread, synchronizing (joining) with the second
 * thread before returning.
 */

/**
 * Start the disk writer running in a new thread, then wait for it to
 * signal that it has completed initialization.
 */
int writerInitThreaded(void) {
    writerReady = false;
    pthread_mutex_init  (&readyLock,  NULL);
    pthread_cond_init   (&readyCond,  NULL);
//  readyLock   = PTHREAD_MUTEX_INITIALIZER;
//  readyCond   = PTHREAD_COND_INITIALIZER;

    if (pthread_create(&writerThread, NULL, startWriter, NULL) != 0) {
        perror("P: Failed to initialize writer thread");
        return -1;
    }
    // now wait for the new thread to say that it's ready
    pthread_mutex_lock(&readyLock);
    while(! writerReady) {
        pthread_cond_wait(&readyCond, &readyLock);
    }
    pthread_mutex_unlock(&readyLock);
    return 0;
}

/////////////////////////////////////////////////////////////////////
// DISK WRITER THREAD ///////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////



// INITIALIZATION CODE ////////////////////////////////////

/**
 * This will only return (a) if there is an error or (b) someone stops
 * the event loop.
 */
static void* startWriter (void * arg) {
    if(writerInit() < 0) {
        printf("log writer initialization failed!\n");
    }
    return NULL;
}

static int writerInit(void) {
    /* XXX NEED A SANITY CHECK HERE */
    loop = ev_loop_new( EVFLAG_AUTO );

//  if(setupLibEvAndCallbacks() < 0) {
//      printf("Error starting libevent\n");
//      return -1;
//  }

    // Signal client, writer is ready
    pthread_mutex_lock(&readyLock);
    writerReady = true;
    pthread_cond_signal(&readyCond);
    pthread_mutex_unlock(&readyLock);

    // LOG(1, ("Writer init complete\n"));

    ev_loop(loop, 0);   // start the loop; this should never return
    return 0;
}

