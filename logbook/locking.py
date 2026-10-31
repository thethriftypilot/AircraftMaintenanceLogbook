"""Serialize entire filesystem/database operations across threads and processes."""
from contextlib import contextmanager
from pathlib import Path
import threading
import os

_states={}
_guard=threading.Lock()

@contextmanager
def operation(root):
    key=str(Path(root).resolve()).casefold()
    with _guard:state=_states.setdefault(key,{'lock':threading.RLock(),'depth':0})
    with state['lock']:
        if state['depth']==0:
            handle=open(Path(root)/'operation.lock','a+b')
            handle.seek(0);handle.write(b'0');handle.flush();handle.seek(0)
            try:
                if os.name=='nt':
                    import msvcrt
                    msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
                else:
                    import fcntl
                    fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except OSError:
                handle.close();raise ValueError('This data directory is busy in another process. Retry after it finishes.') from None
            state['handle']=handle
        state['depth']+=1
        try:yield
        finally:
            state['depth']-=1
            if state['depth']==0:
                handle=state.pop('handle')
                if os.name=='nt':
                    handle.seek(0);msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
                else:fcntl.flock(handle,fcntl.LOCK_UN)
                handle.close()
