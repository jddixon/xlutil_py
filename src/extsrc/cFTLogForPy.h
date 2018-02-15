/* cFTLogForPy.h */

#ifndef _C_FT_LOG_FOR_PY_H_
#define _C_FT_LOG_FOR_PY_H_

// we need something like -I /usr/include/python2.7 on the command line
// if this isn't first, expect _POSIX_C_SOURCE redefined warnings
#include <Python.h>

/* pthread specs require that this be #included first */
#include <pthread.h>

#include <structmember.h>

#include <errno.h>
#include <ev.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>     // calloc and such
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

/* maximum number of open log files */
#define CLOG_MAX_LOG   (16)

// how often we write the log to disk, in seconds
#define WRITE_INTERVAL  (0.1)

#define LOG_BUFFER_SIZE (4*4096)
#define ACTIVE_BUF      (1)
#define FULL_BUF        (2)
#define BEING_WRITTEN   (3)
#define READY_BUF       (4)

#define PADBYTES (1024)
typedef struct _logPage {
    unsigned char*  data;
    uint16_t        offset;         // to first free byte
    uint16_t        pageBytes;      // K * LOG_PAGE_SIZE
    uint16_t        flags;
} logBufDesc_t;


/*
*/

#define PATH_SEP '/'
#define MAX_PATH_LEN (256)
#define C_FT_LOG_BUF_COUNT (4)

/*
 * This is a data structure allocated for each log in use.  The data structure
 * must be initialized before use and deallocated on close().
 *
 * Presumably need to align this
 *
 */
typedef struct _c_log_ {

    logBufDesc_t        logBufDescs[C_FT_LOG_BUF_COUNT];
    unsigned char       logBuffers[C_FT_LOG_BUF_COUNT * LOG_BUFFER_SIZE];

    // GCC insists upon all the parentheses
    char                logDir [MAX_PATH_LEN+1] __attribute__((aligned(16)));
    char                logName[MAX_PATH_LEN+1] __attribute__((aligned(16)));
    u_int32_t           fd                      __attribute__((aligned(16)));
    u_int32_t           count;          // number of messages written

    ev_timer            t_watcher;      // timed write to disk

    // buffer write flags 
#   define WRITE_PENDING     (0x0001)
#   define WRITE_IN_PROGRESS (0x0002)
    u_int32_t           writeFlags;

    u_int32_t           bufInUse;       // which buffer we are using
    pthread_mutex_t     logBufLock;     // = PTHREAD_MUTEX_INITIALIZER;
} cFTLogDesc_t;


// GLOBALS //////////////////////////////////////////////////////////
extern int    secondThreadStarted;
extern struct ev_loop* loop;

extern int logNdx;              // one less than the number of logs open
extern cFTLogDesc_t* logDescs[CLOG_MAX_LOG];

extern pthread_t            writerThread;
// extern int               writerReady;
// extern pthread_mutex_t   readyLock;
// extern pthread_cond_t    readyCond;

// PROTOTYPES ///////////////////////////////////////////////////////
extern void initLogDescs(void);
extern int openLogFile(const char* pathToLog) ;
extern void cLogDealloc(int ndx);
extern int  setupLibEvAndCallbacks(int);

extern int   initLogBuffers(int);
extern int   writerInitThreaded(void);

// MODULE-LEVEL METHODS ////////////////////////////////////

PyObject* init_cft_logger(PyObject* self, PyObject* args);
PyObject* open_cft_log(PyObject* self, PyObject* args);
PyObject* close_cft_logger(PyObject* self, PyObject* args);
PyObject* log_msg(PyObject* self, PyObject* args);

// WRAPPED FUNCTIONS //////////////////////////////////////
int  _open_cft_log(const char* pathToLog);
void _log_msg(const int ndx, const char* msg);


#endif /* _C_FT_LOG_FOR_PY_H_ */
