/* ~/dev/py/xlutil_py/src/extsrc/evLoop.c */

#include "cFTLogForPy.h"

// DATA /////////////////////////////////////////////////////////////

// EVENT LOOP /////////////////////////////////////////////
struct ev_loop* loop;


// CALLBACKS ////////////////////////////////////////////////////////
/**
 * Expect to enter this with the WRITE_PENDING flag set.
 */
static void
timedWriterCB(EV_P_ struct ev_timer *w, int revents) {
    cFTLogDesc_t* d = logDescs[logNdx];

    /* XXX THIS IMPLEMENTATION does not handle FULL pages */

    // get a lock on the descriptor
    pthread_mutex_lock(&d->logBufLock);         // LOCK LOCK LOCK 
    d->writeFlags &= ~WRITE_PENDING; 

    // bufInUse is a logical pointer to the buffer currently in use
    logBufDesc_t* p = d->logBufDescs + d->bufInUse;
    if ( p->offset > 0 ) {
        p->flags        = BEING_WRITTEN;
        d->writeFlags  |= WRITE_IN_PROGRESS; 
        pthread_mutex_unlock(&d->logBufLock);   // UNLOCK UNLOCK  

//      // DEBUG
//      char msg[512];
//      sprintf(msg, "callback flushing %d bytes to disk\n", p->offset);
//      int msgLen = strlen(msg);
//      write (d->fd, msg, msgLen);
//      // END

        d->bufInUse = (d->bufInUse + 1) % C_FT_LOG_BUF_COUNT;

        // XXX if next page isn't READY, we are in serious trouble

        // write buffer to disk - this blocks, of course
        int bytesWritten = write(d->fd, p->data, p->offset);
        if (bytesWritten == -1)
            perror ("timedWriterCB, flushing to disk");

        int status  = fsync(d->fd);
        if (status)
            perror("fsync, flushing log buffer in callback");

        // mark the page as ready for re-use
        pthread_mutex_lock(&d->logBufLock);    // LOCK LOCK
        p->flags    = READY_BUF;
        p->offset   = 0;

        // CLEAR THE WRITE-IN_PROGRESS FLAG
        d->writeFlags &= ~WRITE_IN_PROGRESS; 
        pthread_mutex_unlock(&d->logBufLock);  // UNLOCK UNLOCK
    } else {
        // DEBUG
        // printf("callback: nothing to do, zero offset\n");
        // END
        // just release the lock; there is nothing to do
        pthread_mutex_unlock(&d->logBufLock);  // UNLOCK UNLOCK UNLOCK //
    }

    // schedule the next callback   XXX DROP THIS CODE XXX
    ev_timer_init(&d->t_watcher, 
                                    timedWriterCB, WRITE_INTERVAL, 0);
    ev_timer_start(loop, &d->t_watcher);
}  

// INITIALIZATION CODE //////////////////////////////////////////////

int setupLibEvAndCallbacks(int ndx) {
    ev_timer_init(&logDescs[ndx]->t_watcher, timedWriterCB, 0.1, 0);
    ev_timer_start(loop, &logDescs[ndx]->t_watcher);
    // DEBUG
    // printf ("setup watcher for libNdx %d\n", ndx);
    // END
    return 0;
} 

// HACKING ABOUT ////////////////////////////////////////////////////

int scheduleWrite(int ndx) {
    cFTLogDesc_t* d = logDescs[logNdx];
    pthread_mutex_lock(&d->logBufLock);  // get a lock on the descriptor

    if (!(d->writeFlags & WRITE_PENDING)) {
        // no write pending, so schedule one
        ev_timer_init(&d->t_watcher, timedWriterCB, 0.1, 0);
        ev_timer_start(loop, &d->t_watcher);
        // DEBUG
        // printf ("setup watcher for libNdx %d\n", ndx);
        // END
        d->writeFlags |= WRITE_PENDING; 
    }
    pthread_mutex_unlock(&d->logBufLock);   // unlock the descriptor
    return 0;
}
