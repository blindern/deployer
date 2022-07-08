from contextlib import contextmanager

from NamedAtomicLock import NamedAtomicLock


class ServiceLocks:
    @contextmanager
    def hold_lock(self, name: str):
        lock = NamedAtomicLock(f"deployer-lock-{name}", maxLockAge=900)

        try:
            lock.acquire()
            yield
        finally:
            lock.release()
