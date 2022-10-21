from threading import Timer
from typing import Callable, Dict

timers: Dict[int, Timer] = dict()

def schedule(interval: float, fn: Callable[[], None], id: int = None) -> int:
	if not id:
		id = hash(fn)
		timers[id] = None

	if id in timers:
		fn()

		if id in timers:
			t = Timer(interval, lambda: schedule(interval, fn, id))
			timers[id] = t
			t.start()

	return id

def deschedule(fn):
	id = hash(fn)
	t = timers[id]

	timers.pop(id)
	t.cancel()