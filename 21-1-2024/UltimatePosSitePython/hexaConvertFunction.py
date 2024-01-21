from functools import reduce

def string2hex(param):
    list = []
    for ch in param:
        st2hx = hex(ord(ch)).replace('0x', '')
        if len(st2hx) == 1 :
            st2hx = '0' + st2hx
        list.append(st2hx)
    return reduce(lambda i, j: i+j, list)



def int2hex(param):
    int2hx = hex(param)
    int2hx = int2hx.replace('0x', '')
    return reduce(lambda i, j: i+j, int2hx)



# print(string2hex('15'))

# print(string2hex('الجواهري العربي'))


# 62764462c64862764763164a2062764463963162864a
# $seller_length = strlen($seller_name);
# $seller_length_hexa =  $seller_length < 16 ? '0' . dechex($seller_length) : dechex($seller_length);
# $seller_comp =  '01' . $seller_length_hexa  . bin2hex($seller_name);

# print(string2hex('الجواهري العربي'))