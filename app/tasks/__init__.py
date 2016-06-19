from threading import Timer


def execute_callback_after_time(delay_seconds, callback, kwargs={}):
    '''
    After delay_seconds seconds, executes the callback
    with the given keyword args.
    Returns the timer so that it can be stopped with cancel
    '''
    t = Timer(delay_seconds, callback, kwargs=kwargs)
    t.start()
    return t
