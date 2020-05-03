import asyncio


def make_function_async(funcname):
    """Make coroutine from function"""
    if isinstance(funcname, str):
        if funcname in globals():
            funcname = globals()[funcname]
        elif funcname in locals():
            funcname = locals()[funcname]
        else:
            raise ValueError("parameter must be a callable function or function name str in locals() or globals()")

    if callable(funcname):
        # return await asyncio.coroutine(funcname)()
        return asyncio.coroutine(funcname)
