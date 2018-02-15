/* ~/dev/py/xlutil_py/extsrc/logBufs.c */

#include "cFTLogForPy.h"

// local prototypes 
static cFTLogDesc_t* cLogAllocInit(const char* logDir, const char* logName);

int initLogBuffers(ndx) {
    memset(logDescs[ndx]->logBufDescs, 0, 
                                C_FT_LOG_BUF_COUNT * sizeof(logBufDesc_t));

    // paranoia is good for the soul
    pthread_mutex_lock(&logDescs[ndx]->logBufLock);
    int i;
    for (i = 0; i < C_FT_LOG_BUF_COUNT; i++) {
        logBufDesc_t* p = logDescs[ndx]->logBufDescs + i;
        p->flags = i == 0 ? ACTIVE_BUF : READY_BUF;
        p->pageBytes = LOG_BUFFER_SIZE;
        p->data      = logDescs[ndx]->logBuffers + i * LOG_BUFFER_SIZE;
    }

    // ndx of page in use has already been set to zero
    pthread_mutex_unlock(&logDescs[ndx]->logBufLock);
    return 0;
}

// we extract the name of the log directory from s and write it into logDir
static
int splitPath(char* logDir, char* logName, const char *s) {
    int len = strlen(s);
    if (len > MAX_PATH_LEN)
        return ENAMETOOLONG;
    const char* end = s + len;        // first character beyond

    bool foundIt = false;
    const char *p;
    for ( p = end - 1; p >= s; p--)
        if (*p == PATH_SEP) {
            foundIt = true;
            break;
        }
    if (foundIt) {
        size_t pathLen = p - s;
        if (pathLen > 0)
            memcpy( logDir, s, pathLen );
        logDir[ pathLen ] = 0;

        size_t nameLen = end - p - 1;
        if (nameLen > 0)
            memcpy( logName, p + 1, nameLen );
        logName[ nameLen ] = 0;
        return 0;
    } else {
        return -1;
    }
}

/**
 * Confirm that this specific directory exists; if it doesn't, create
 * it.  Return 0 if OK, a negative number otherwise.
 */
static int checkDir(const char* pathToDir) {
    struct stat buffer;
    int status = stat(pathToDir, & buffer);
    if (status) {
        if (errno == ENOENT) {
            // no such directory: create it
            status = mkdir(pathToDir, 0744);      // ??? 0644 ???
        }
        // any other errno is a real error
    } else {
        // file exists; if it's a directory, return 0
        if (S_ISDIR(buffer.st_mode))
            status = 0;
        else
            status = -1;
    }
    return status;
}
/**
 * Confirm that the path to the log directory exists, creating any
 * intervening directories if necessary.
 *
 * We assume that higher-level logic has done sensible checks.  In
 * particular, we do not check for leading or internal double dots ('..').
 */
static
int checkDirs(const char* pathToLog) {
    char path[MAX_PATH_LEN + 1];
    strncpy (path, pathToLog, MAX_PATH_LEN);

    int status  = 0;
    int len     = strlen(path);
    char *end   = path + len;
    // XXX DOESN'T WORK IF NO SLASH
    char *p = path ;
    // do NOT check whether first char is /
    for (p++ ; p < end; p++)
        if (*p == '/') {
            *p = 0;
            if( (status = checkDir(path)) )
                break;
            *p = '/';
        }
    status = checkDir(path);
    return status;
}


/** Deallocates a single descriptor */
// static 
void cLogDealloc(int ndx) {
    cFTLogDesc_t* cLog = logDescs[ndx];
    if (cLog != NULL) {
        free(cLog);
        // printf("*** cLog deallocated desc %d successfully ***\n", ndx);
        logDescs[ndx] = NULL;
    }

}

void initLogDescs(void) {
    int i;
    for (i = 0; i < CLOG_MAX_LOG; i++)
        logDescs[i] = NULL;
} 


/**
 * This is called once for each log file added.  It returns an index
 * into the logDescs table.
 */
static 
cFTLogDesc_t* cLogAllocInit(const char* logDir, const char* logName) {
    // XXX CHECK FOR NULL OR OUTSIZED PARAMETERS XXX
    cFTLogDesc_t* cLog = calloc(1, sizeof(cFTLogDesc_t));
    if (cLog != NULL) {
        // this cannot be set with PTHREAD_MUTEX_INITIALIZER because it isn't
        // static; and similarly for the next two fields
//      pthread_mutex_init  (&cLog->readyLock,  NULL);
//      pthread_cond_init   (&cLog->readyCond,  NULL);
        pthread_mutex_init  (&cLog->logBufLock, NULL);

        memcpy( cLog->logDir,  logDir,  strlen(logDir) );
        memcpy( cLog->logName, logName, strlen(logName) );

        // printf("*** cLog allocated and initialized ***\n");
    }
    return cLog;            // which may be NULL
}

/**
 * Split the pathToLog to get the path to the directory and the name of
 * the log file.  Verifies that the log directory exists and then opens
 * the log file.
 *
 * If the log file can be opened, returns its
 * (fd).  Otherwise returns -1 and sets errno.
 */
// static
int openLogFile(const char* pathToLog) {
    char logDir [MAX_PATH_LEN + 1];
    char logName[MAX_PATH_LEN + 1];
    int  logFD = -1;
    if (pathToLog == NULL)
        return -1;
    int status = splitPath(logDir, logName, pathToLog);
    if (!status)
        status = checkDirs(logDir);
    if (!status) {
        // O_APPEND _must_ be accompanied by O_WRONLY or O_RDWR
        status  = logFD
                = open(pathToLog, O_CREAT | O_APPEND | O_WRONLY,
                                S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
        cFTLogDesc_t* sd   = cLogAllocInit(logDir, logName);
        sd->fd           = logFD;
        logDescs[logNdx] = sd;

    }
    return status;
}
