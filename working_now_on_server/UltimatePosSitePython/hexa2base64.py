import codecs

def hex2funbase64(param):
    result = codecs.encode(codecs.decode(param, 'hex'), 'base64').decode()
    return result

# print(hex2funbase64(str('010F62764462c64862764763164a2062764463963162864a')))






# $seller_name = get_bloginfo( 'name' );
# $invoice_total = $order->get_total();
# $vat_value = $order->get_total_tax();
#
# $seller_length = strlen($seller_name);
# $seller_length_hexa =  $seller_length < 16 ? '0' . dechex($seller_length) : dechex($seller_length);
# $seller_comp =  '01' . $seller_length_hexa  . bin2hex($seller_name);
#
# $vat_num_length = strlen($uso_tax_number);
# $vat_num_length_hexa =  $vat_num_length < 16 ? '0' . dechex($vat_num_length) : dechex($vat_num_length);
# $vat_num_comp = '02' . $vat_num_length_hexa  . bin2hex($uso_tax_number);
#
# $new_date_length = strlen($new_date);
# $new_date_length_length_hexa =  $new_date_length < 16 ? '0' . dechex($new_date_length) : dechex($new_date_length);
# $new_date_comp =  '03' . $new_date_length_length_hexa  . bin2hex($new_date);
#
# $invoice_length = strlen($invoice_total);
# $invoice_length_hexa =  $invoice_length < 16 ? '0' . dechex($invoice_length) : dechex($invoice_length);
# $test_invoice_comp = '04' . $invoice_length_hexa  . bin2hex($invoice_total);
#
# $vat_value_length = strlen($vat_value);
# $vat_value_length_hexa =  $vat_value_length < 16 ? '0' . dechex($vat_value_length) : dechex($vat_value_length);
# $vat_value_comp = '05' . $vat_value_length_hexa  . bin2hex($vat_value);
#
# $total_hex =  $seller_comp . $vat_num_comp . $new_date_comp . $test_invoice_comp . $vat_value_comp;
# $QR_code = base64_encode(hex2bin($total_hex));
#
# ?>
# <img src="https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=<?php echo $QR_code; ?>&choe=UTF-8"
# title="Link to Google.com"/>

# AQ9idkRixkhidkdjFkogYnZEY5YxYoZK
#
#
# AR3Yp9mE2KzZiNin2YfYsdmKINin2YTYudix2KjZig==


# ASHYp9mE2YXYqtis2LEg2KfZhNin2YTZg9iq2LHZiNmG2Yo=
# YnZEZFYqYsYxIGJ2RGJ2RGQ2KmMWSGRmSg==
# ARFidkRkVipixjEgYnZEYnZEZDYqYxZIZGZK
# YnZEZFYqYsYxIGJ2RGJ2RGQ2KmMWSGRmSg==




# AQVBaG1lZA==
#
# AQVBaG1lZA==
