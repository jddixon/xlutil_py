/* ~/dev/py/xlutil_py/extfunc/modFunc.c */

#include "cFTLogForPy.h"

PyObject* init_cft_logger(PyObject* self, PyObject* args) {
    // INIT GLOBALS
    logNdx              = -1;           // 0-based current index
    secondThreadStarted = false;        // XXX SHOULD NOT NEED THIS

    // init local variables
    int status = 0;
    initLogDescs();         // clears descriptor table

    status = writerInitThreaded();
    if (!status)
        secondThreadStarted = true;
    return Py_BuildValue("i", status);
}

/**
 * Open a log file given a path to it.  Returns a negative error code
 * or a non-negative log index.
 *
 * NOTE that the name begins with an underscore (_).
 */
int _open_cft_log(const char* pathToLog) {
    int status = 0;
    logNdx++;                               // USED in openLogFile
    int fd = openLogFile(pathToLog);
    if (fd < 0) {
        status = -1;
        char str[512];
        sprintf(str, "openClog: opening log file '%s'", pathToLog);
        perror(str);
    }
    if (!status)
        status = initLogBuffers(logNdx);
    if(!status)
        status = setupLibEvAndCallbacks(logNdx);
    if (status < 0) {
        logNdx--;
        return status;
    } else {
        return logNdx;
    }
}
PyObject* open_cft_log(PyObject* self, PyObject* args) {
    char* pathToLog;
    if (!PyArg_ParseTuple(args, "s", &pathToLog))
        return NULL;
    int status = _open_cft_log(pathToLog);
    return Py_BuildValue("i", status);
}

PyObject* close_cft_logger(PyObject* self, PyObject* args) {

    // we'll just ignore any arguments
    int status = 0;

    // shut down any watchers ---------------------------------------
    int ndx;
    for (ndx = 0; ndx <= logNdx; ndx++)
        ev_timer_stop(loop, &logDescs[ndx]->t_watcher);

    // if write is in progress, wait for it to complete -------------
    // LATER: we will just wait two WRITE_INTERVAL; this may or may
    // not make sense !
    double twoWrites = 4 * WRITE_INTERVAL;      // HACK: 4 INSTEAD OF TWO
    struct timespec ts;
    ts.tv_sec  = (int)twoWrites;        // integer part; this will be zero
    // the next line converts the fractional part of twoWrites to ns
    ts.tv_nsec = ( twoWrites - ts.tv_sec ) * 1000000000;

    //printf ("sleeping %lds, %ldns\n", ts.tv_sec, ts.tv_nsec); fflush(stdout);

    nanosleep(&ts, NULL);

    // stop the background event loop -------------------------------
    // printf("  DESTROYING event loop\n"); fflush(stdout);
    ev_loop_destroy(loop);          // we created it, so this is safe
    // printf("  ... event loop destroyed\n"); fflush(stdout);

    // we get (25% of the time with twoWrites = 3; 10% with 6; 20% with 10)
    //     (libev) epoll_wait: Bad file descriptor
    // and some point after this

    // wait for the logger thread to stop ----------------------------
    int e = pthread_join(writerThread, NULL); // returns error number
    if (e)
        perror("join with writer thread");

    // printf("JOIN COMPLETE\n");      fflush(stdout);

    //===============================================================
    // XXX SEGFAULT but empty log file if we return here ============
    // If you use gdb python and then run testLogMgr.py you can see
    // that the segfault is related to a 'no such file or directory'
    // error, which gdb connects to line 4439 in malloc.c
    //
    // Review of the code shows that the log file is opened in the main
    // thread, written in the writerThread, and then flushed and closed
    // back in the main thread.  It would seem cleaner to do all file
    // IO in one thread, the writerThread.  This might also get rid
    // of this strange bug!!
    //===============================================================


    // POSSIBLE WRITE TO DISK FROM MAIN THREAD //////////////////////

    // flush any pending messages to disk ---------------------------
    for (ndx = 0; ndx <= logNdx; ndx++) {
        logBufDesc_t* p = &logDescs[ndx]->logBufDescs[logDescs[ndx]->bufInUse];

        if ( p->offset > 0 ) {
            // write buffer to disk
            p->flags         = BEING_WRITTEN;
            int bytesWritten = write(logDescs[ndx]->fd, p->data, p->offset);
            if (bytesWritten == -1) {
                perror ("closeLog, writing log buffer to disk");
            }
            status  = fsync(logDescs[ndx]->fd);
            if (status)
                perror("fsync to fd");
        }
        // printf("ABOUT TO ACTUALLY CLOSE LOG FILE %d\n", ndx);
        // close the log file -------------------------------------------
        if (!status && (logDescs[ndx]->fd >= 0)) {
            status = close(logDescs[ndx]->fd);
        }
    }
    // release any resources allocated
    // HACK - the twoWrites sleep above considerably reduced the number of
    // bad FD faults; adding this back in appears to have eliminated them
    usleep(5000*1000);
    // END`

    // if the status is non-zero we nevertheless close all files
    for ( ; logNdx >= 0; logNdx--)
        cLogDealloc(logNdx);

    // the PY_BuildValue should convert a plain old C int to a Python integer
    return Py_BuildValue("i", status);
}


/**
 * Write a log message.
 *
 * Parameters are buffer index (ndx) and a properly terminated message
 * (msg), one with a newline and a terminating null byte.  These are
 * packaged up Pythonically and dissected here using PyArg_ParseTuple,
 * with a format string "is" used to guide the parse.  We trust that
 * the Python code has vetted the parameters.
 *
 * Pathological cases, such as the message being larger than any buffer,
 * may cause unpredictable behavior.
 */

PyObject* log_msg(PyObject* self, PyObject* args) {
    int     ndx;
    const   char* msg;

    // logNdx is now first parameter
    if (!PyArg_ParseTuple(args, "is", &ndx, &msg))
        return NULL;
    if (msg)
        _log_msg(ndx, msg);
    Py_RETURN_NONE;
}
/**
 * Low-level write a log message function.  ndx is an index into the
 * logDescs descriptor table.  msg is a null-terminated C string.
 */
void _log_msg(const int ndx, const char* msg) {
    // XXX should make sure that ndx value is sensible
    int len = strlen(msg);

    // get the mutex
    pthread_mutex_lock(&logDescs[ndx]->logBufLock);

    // if msg will not fit, mark current page as FULL, find next
    // available page, and mark that ACTIVE.
    logBufDesc_t* p = &logDescs[ndx]->logBufDescs[logDescs[ndx]->bufInUse];
    if (p->offset + len >= p->pageBytes) {
        p->flags    = FULL_BUF;
//          // DEBUG
//          printf("buffer %d at offset %d is FULL\n",
//                      logDescs[ndx]->bufInUse, p->offset);
//          fflush(stdout);
//          // END
        logDescs[ndx]->bufInUse =
                    (logDescs[ndx]->bufInUse + 1) % C_FT_LOG_BUF_COUNT;
        /* RISK OF INFINITE LOOP */
        // XXX This risk is real: we sometimes get an infinite loop
        for (p = &logDescs[ndx]->logBufDescs[logDescs[ndx]->bufInUse];
                    p->flags != READY_BUF;
                    p = &logDescs[ndx]->logBufDescs[logDescs[ndx]->bufInUse] )
            logDescs[ndx]->bufInUse =
                    (logDescs[ndx]->bufInUse + 1) % C_FT_LOG_BUF_COUNT;
    }
    // write msg to active page and update offset; NOT null-terminated
    memcpy(p->data + p->offset, msg, len);
    p->offset += len;

    // step the message count and release the mutex
    logDescs[ndx]->count++;
    pthread_mutex_unlock(&logDescs[ndx]->logBufLock);
}
