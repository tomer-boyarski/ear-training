def func_kwargs(**kwargs):
    print('kwargs: ', kwargs)
    print('type: ', type(kwargs))


func_kwargs(key1=1, key2=2, key3=3)