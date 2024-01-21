function razorpayPaymentScript ( data, get_price_of_package, pos_no, sub_type, type ) {
    var options = {
        "key": "rzp_live_fg6d0mseHGoSRL", // Enter the Key ID generated from the Dashboard
        "amount": data.amount * 100, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
        "currency": "INR",
        "name": "sameer",
        "description": "Cashier Me payment",
        "image": "https://cashierme.com/static/assets/img/uposNav.png",
        "order_id": data.id, //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
        "handler": function ( response ) {
            if ( type=="upgrade_pos_no" ) {
                $.ajax ( {
                    type: 'POST',
                    url: '/india_success_upgrade_pos/' + get_price_of_package + '/' + pos_no + '/' + sub_type + '/' + response.razorpay_order_id + "/" + response.razorpay_payment_id + "/" + response.razorpay_signature,
                    success: function ( data ) {
                        $ ( "#divBlockLoader" ).show ()
                        window.location.reload ()
                    }
                } )
            }
            if ( type=="upgrade_to_annually" ) {
                $.ajax ( {
                    type: 'POST',
                    url: '/india_update_subscription_to_annually/' + pos_no + '/' + response.razorpay_order_id + "/" + response.razorpay_payment_id + "/" + response.razorpay_signature,
                    success: function ( data ) {
                        $ ( "#divBlockLoader" ).show ()
                        window.location.reload ()
                    }
                } )
            }
            if ( type=="renew_subscription" ) {
                $.ajax ( {
                    type: 'POST',
                    url: '/upgrade_subscription_india/'+ response.razorpay_order_id + "/" + response.razorpay_payment_id + "/" + response.razorpay_signature ,
                    success: function ( data ) {
                        $ ( "#divBlockLoader" ).show ()
                        window.location.reload ()
                    }
                } )
            }
        },
        "theme": {
            "color": "#4d7c94"
        }
    };
    var rzp1 = new Razorpay ( options );
    rzp1.on ( 'payment.failed', function ( response ) {
        $ ( "#divBlockLoader" ).show ()
        window.location.reload ()
    } );
    rzp1.open ();
    this.preventDefault ();

}

var country_code_id = document.getElementById ( "countryCodeId" ).value;
var modal = document.getElementById ( "myModal" );
var btn = document.getElementById ( "myBtn" );
var span = document.getElementsByClassName ( "close" )[ 0 ];

function renewSubscription(){
    var alert_card_message= document.getElementById ('renew_subscription_message')

    document.getElementById('renewButton').style.display = 'none'
    $ ( "#image_reload" ).show ()
    if( country_code_id == "GLB" || country_code_id == "MYS"||country_code_id == "EGY"){
        window.location.href="/upgrade_subscription_renew"
    }
    if(country_code_id == "TUR"){
        window.location.href="#popup1"
    }
    if(country_code_id == "IND"){
        $.ajax ( {
            type: 'POST',
            url: '/renew_india_subscription',
            success: function ( data ) {
                razorpayPaymentScript ( data, "", "", "", "renew_subscription" )
            }
        } )
    }
    if(country_code_id == "SAU"){
        $.ajax ( {
            type: 'POST',
            url: '/update_subscription_form_user_dashboard',
            success: function ( data ) {
                if (data['status'] == "success"){
                    $ ( "#image_reload" ).hide ()
                    window.location.href = "/view_invoice/"+data['order_id']
                }if (data['status'] == "invalid" || data['status'] == "error" ){
                    $ ( "#image_reload" ).show ()
                    alert_card_message.style.display = 'block'
                    alert_card_message.innerText = data['msg']

                }

            }
        } )

    }
}

function renew_turkish_subscription(){
    var Card_Number= document.getElementById ('Card_Number')
    var Card_Name= document.getElementById ('Card_Name')
    var expirymonth= document.getElementById ('expirymonth')
    var expiryyear= document.getElementById ('expiryyear')
    var Card_CvC= document.getElementById ('Card_CvC')
    var alert_card_message= document.getElementById ('alert_card_message')
    if (Card_Number.value && Card_Name.value && expirymonth.value && expiryyear.value && Card_CvC.value != "" ){
        $.ajax ( {
                type: 'POST',
                url: '/paymentCardSubmit/'+Card_Number.value + "/"+Card_Name.value+ "/"+ expirymonth.value+ "/"+expiryyear.value + "/"+ Card_CvC.value,
                success: function ( data ) {
                    if (data['status'] == "Success"){
                        $ ( "#image_reload" ).hide ()
                        window.location.href = "/view_invoice/"+data['order_id']
                    } if (data['status'] == "Failed"){
                        $ ( "#image_reload" ).hide ()
                        alert_card_message.style.display = 'block'
                        alert_card_message.innerText = "üzgünüm, şimdi işlem yapamam lütfen mektubu tekrar deneyin veya ödeme kartını değiştirin"
                    }if (data['status'] == "Error"){
                        $ ( "#image_reload" ).hide ()
                        Card_Number.style.border="1px solid red"
                        alert_card_message.style.display = 'block'
                        alert_card_message.innerText = "geçersiz kart numarası"
                    }if (data['status'] == "function_error"){
                        $ ( "#image_reload" ).hide ()
                        alert_card_message.style.display = 'block'
                        alert_card_message.innerText = "üzgünüm, şimdi işlem yapamam lütfen mektubu tekrar deneyin veya ödeme kartını değiştirin"
                    }
                },
            beforeSend: function () {
                    $ ( "#image_reload" ).show ()
                },
            } )
    }
    if(Card_Number.value == ""){
        Card_Number.style.border = "1px solid red"

    }else{
        Card_Number.style.border = "1px solid #e9ecef"
    }
    if(Card_Name.value == ""){
        Card_Name.style.border = "1px solid red"

    }else{
        Card_Name.style.border = "1px solid #e9ecef"
    }
    if(expirymonth.value == ""){
        expirymonth.style.border = "1px solid red"

    }else{
        expirymonth.style.border = "1px solid #e9ecef"
    }
    if(expiryyear.value == ""){
        expiryyear.style.border = "1px solid red"

    }else{
        expiryyear.style.border = "1px solid #e9ecef"
    }
    if(Card_CvC.value == ""){
        Card_CvC.style.border = "1px solid red"

    }else{
        Card_CvC.style.border = "1px solid #e9ecef"
    }



}







btn.onclick = function () {
    modal.style.display = "block";
    clickButtonsTest ()
}
span.onclick = function () {
    modal.style.display = "none"
}
window.onclick = function ( event ) {
    if ( event.target==modal ) {
        modal.style.display = "none"
    }
};
var model_cancel = document.getElementById ( "myModal_cancel_subscription" );
var btn_cancel = document.getElementById ( "cancel_sub_button" );
var span_cancel = document.getElementsByClassName ( "close-popup-cancel" )[ 0 ];
btn_cancel.onclick = function () {
    model_cancel.style.display = "block"
}
span_cancel.onclick = function () {
    model_cancel.style.display = "none"
}
window.onclick = function ( event ) {
    if ( event.target==model_cancel ) {
        model_cancel.style.display = "none"
    }
};
var model_cancel_alert = document.getElementById ( "myModal_alert_subscription" );
var btn_alert = document.getElementById ( "notification_click" );
var sqpn_alert = document.getElementsByClassName ( "close-popup-alert" )[ 0 ];
btn_alert.onclick = function () {
    model_cancel_alert.style.display = "block"
}
sqpn_alert.onclick = function () {
    model_cancel_alert.style.display = "none"
}
window.onclick = function ( event ) {
    if ( event.target==model_cancel_alert ) {
        model_cancel_alert.style.display = "none"
    }
};

function confirm_order () {
    const pos_unm = document.getElementById ( "pos_num" ).value;
    var url_methods = ""

    if(country_code_id == "TUR"){
        url_methods = "/update_subscription_to_yearly_turkish/"
    }if(country_code_id != "TUR"){
        url_methods = "/update_subscription_to_yearly/"

    }

    if ( pos_unm=='' || pos_unm==null ) {
        const pos_unm_alert = document.getElementById ( "pos_num" )
        pos_unm_alert.style.border = '2px solid red'
    }
    ;
    if ( pos_unm!='' ) {
        if ( country_code_id!="IND" ) {
            $.ajax ( {
                type: 'POST',
                url: url_methods + pos_unm,
                success: function ( data ) {
                    var data = data
                    if ( data.status=='success' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#success_process_message" ).show ()
                        window.location.href = '/view_invoice/' + data.value
                    }
                    if ( data=='customer_havenot_money' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_enough_money" ).show ()
                    }
                    if ( data=='Cant_process_now' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                    if ( data=='get_code_error' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                    if ( data=='error_for_request' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                },
                beforeSend: function () {
                    $ ( "#cancel_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#confirm_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#reloading_image_gif_annual" ).show ()
                },
            } )

        }
        if ( country_code_id=="IND" ) {
            var get_price_of_package = "10"
            $.ajax ( {
                type: 'POST',
                url: '/india_upgrade_pos_monthly/' + get_price_of_package + '/' + pos_unm + '/' + "yearly",
                success: function ( data ) {
                    razorpayPaymentScript ( data, get_price_of_package, pos_unm, "yearly", "upgrade_to_annually" )

                },
                beforeSend: function () {
                    $ ( "#cancel_Addpos_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#confirm_Addpos_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#reloading_image_gif_annual" ).show ()
                },
            } )

        }

    }
};

function confirm_button_monthly () {
    const pos_unm = document.getElementById ( "pos_num_Tomonthly" ).value;
    if ( pos_unm=='' || pos_unm==null ) {
        const pos_unm_alert = document.getElementById ( "pos_num_Tomonthly" )
        pos_unm_alert.style.border = '2px solid red'
    }
    ;
    if ( pos_unm!='' ) {
        $.ajax ( {
            type: 'POST',
            url: '/update_subscription_to_monthly/' + pos_unm,
            success: function ( data ) {
                if ( data=='ok' ) {
                    $ ( "#close-popup" ).click ()
                    $ ( "#message_success_annualyToMonthly" ).show ()
                    cancel_order ()
                }
            }
        } )
    }
};

function cancel_order () {
    $ ( "#close-popup" ).click ()
    $ ( "#models_popup_links" ).click ()
};

function subscription_to_Monthly () {
    $ ( "#pos_text" ).show ()
    $ ( "#pos_num_Tomonthly" ).show ()
    $ ( "#confirm_button_monthly" ).show ()
    $ ( "#cancel_button_monthly" ).show ()
    $ ( "#price_text_month" ).show ()
    $ ( "#subscription_button_monthly" ).hide ()
    $ ( "#AddMorePos_button_annualy" ).hide ()
    $ ( "#RemoveMorePos_button_annualy" ).hide ()
    $ ( "#links_upgrade_subscription" ).show ()
    calculation_price_Monthly ()
}

function subscription () {
    $ ( "#current_price_text_annualy" ).show ();
    $ ( "#pos_text" ).show ()
    $ ( "#pos_num" ).show ()
    $ ( "#confirm_button" ).show ()
    $ ( "#cancel_button" ).show ()
    $ ( "#price_text" ).show ()
    $ ( "#subscription_button" ).hide ()
    $ ( "#AddMorePos_button" ).hide ()
    $ ( "#RemoveMorePos_button" ).hide ()
    $ ( "#links_upgrade_subscription" ).show ()
    calculation_price_annualy_subscription ()
}

function AddMorePos_button () {
    $ ( "#upgrade_pos_num" ).show ()
    $ ( "#Add_pos_text" ).show ()
    $ ( "#Add_price_text" ).show ()
    $ ( "#AddMorePos_button" ).hide ()
    $ ( "#cancel_Addpos_button" ).show ()
    $ ( "#confirm_Addpos_button" ).show ()
    $ ( "#subscription_button" ).hide ()
    $ ( "#RemoveMorePos_button" ).hide ()
    $ ( "#current_price_text" ).show ()
    $ ( "#links_Addpos" ).show ()
}

function AddMorePos_button_annualy () {
    $ ( "#upgrade_pos_num_annualy" ).show ()
    $ ( "#Add_pos_text_annualy" ).show ()
    $ ( "#Add_price_text_annualy" ).show ()
    $ ( "#AddMorePos_button_annualy" ).hide ()
    $ ( "#cancel_Addpos_button_annualy" ).show ()
    $ ( "#confirm_Addpos_button_annualy" ).show ()
    $ ( "#RemoveMorePos_button_annualy" ).hide ()
    $ ( "#current_price_text_annualy" ).show ()
    $ ( "#links_Addpos" ).show ()
    upgrade_pos_calculation_price_annualy ()
}

function upgrade_pos_calculation_price () {
    const pos_num = document.getElementById ( 'upgrade_pos_num' ).value;
    const package_type = 'Monthly'
    const price = document.getElementById ( 'Add_get_price' )
    const current_price = document.getElementById ( 'get_now_price' )
    const pos_unm_alert = document.getElementById ( "upgrade_pos_num" )
    pos_unm_alert.style.border = '1px solid green'
    pos_unm_alert.style.borderRadius = '10px'
    $.ajax ( {
        type: "POST",
        url: "/get_price_of_package/" + pos_num + '/' + package_type,
        success: function () {
        }
    } ).done ( function ( data ) {
        price.textContent = data.price
        current_price.textContent = data.fullcal
    } )
};

function upgrade_pos_calculation_price_annualy () {
    const pos_num = document.getElementById ( 'upgrade_pos_num_annualy' ).value;
    const package_type = 'yearly'
    const price = document.getElementById ( 'Add_get_price_annualy' )
    const current_price = document.getElementById ( 'get_now_price_annualy' )
    const pos_unm_alert = document.getElementById ( "upgrade_pos_num_annualy" )
    pos_unm_alert.style.border = '1px solid green'
    pos_unm_alert.style.borderRadius = '10px'
    $.ajax ( {
        type: "POST",
        url: "/get_price_of_package/" + pos_num + '/' + package_type,
        success: function () {
        }
    } ).done ( function ( data ) {
        price.textContent = data.price
        current_price.textContent = data.get_amount.toFixed ( 2 )
    } )
};

function calculation_price () {
    const pos_num = document.getElementById ( 'pos_num' ).value;
    const package_type = 'yearly'
    const price = document.getElementById ( 'get_price' )
    const pos_unm_alert = document.getElementById ( "pos_num" )
    pos_unm_alert.style.border = '1px solid green'
    pos_unm_alert.style.borderRadius = '10px'
    $.ajax ( {
        type: "POST",
        url: "/get_price_of_package/" + pos_num + '/' + package_type,
        success: function () {
        }
    } ).done ( function ( data ) {
        price.textContent = data.price
    } )
};

function calculation_price_annualy_subscription () {
    const pos_num = document.getElementById ( 'pos_num' ).value;
    const package_type = 'yearly'
    const price = document.getElementById ( 'get_price' )
    const price_toPayment = document.getElementById ( 'get_now_price_annualy' )
    const pos_unm_alert = document.getElementById ( "pos_num" )
    pos_unm_alert.style.border = '1px solid green'
    pos_unm_alert.style.borderRadius = '10px'
    $.ajax ( {
        type: "POST",
        url: "/get_price_of_package/" + pos_num + '/' + package_type,
        success: function () {
        }
    } ).done ( function ( data ) {
        price.textContent = data.price
        price_toPayment.textContent = data.Balance
    } )
};

function calculation_price_Monthly () {
    const pos_num = document.getElementById ( 'pos_num_Tomonthly' ).value;
    const package_type = 'Monthly'
    const price = document.getElementById ( 'get_price_monthly' )
    const pos_unm_alert = document.getElementById ( "pos_num_Tomonthly" )
    pos_unm_alert.style.border = '1px solid green'
    pos_unm_alert.style.borderRadius = '10px'
    $.ajax ( {
        type: "POST",
        url: "/get_price_of_package/" + pos_num + '/' + package_type,
        success: function () {
        }
    } ).done ( function ( data ) {
        price.textContent = data.price
    } )
};

function closeCancelSubscription () {
    $ ( "#close-popup-cancel" ).click ()
};

function confirmToCancel_Subscription () {
    let status = "null"
    if(document.getElementById('cancel_sub_radio').checked){
        status = "Canceled"
    }else if(document.getElementById('delete_sub_radio').checked){
        status = "Delete"
    }else{
        status = ""
    }
    $.ajax ( {
        type: 'POST',
        url: '/confirm_cancel_subscription/'+ status,
        success: function ( data ) {
            $ ( "#close-popup-cancel" ).click ()
            window.location.reload ()
        }
    } )
}


function upgrade_pos_confirm_order () {
    const get_price_of_package = document.getElementById ( "get_now_price" ).innerText
    const pos_no = document.getElementById ( "upgrade_pos_num" ).value;
    const span_pos_no = document.getElementById ( "pos_monthly_no" )
    const span_create_link = document.getElementById ( "span_create_link" )
    const sub_type = 'Monthly'
    var function_url = ""
    if(country_code_id == "SAU" || country_code_id == "EGY"){
        function_url = "/confirm_upgrade_posNo_subscription_monthly/"

    } if(country_code_id == "TUR"){
        function_url = "/confirm_upgrade_posNo_subscription_monthly_for_turkish/"

    }

    if ( pos_no=='' || pos_no==null ) {
        const pos_unm_alert = document.getElementById ( "upgrade_pos_num" )
        pos_unm_alert.style.border = '2px solid red'
    }
    if ( pos_no!='' ) {
        if ( country_code_id!="IND" ) {
            $.ajax ( {
                type: 'POST',
                url: function_url + get_price_of_package + '/' + pos_no + '/' + sub_type,
                success: function ( data ) {
                    var data = data
                    if ( data.status=='success' ) {
                        window.location.reload ()
                    }
                    if ( data=='customer_havenot_money' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_enough_money" ).show ()
                    }
                    if ( data=='Cant_process_now' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                    if ( data=='get_code_error' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                    if ( data=='error_for_request' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                },
                beforeSend: function () {
                    $ ( "#cancel_Addpos_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#confirm_Addpos_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#reloading_image_gif" ).show ()
                },
            } )
        }
        if ( country_code_id=="IND" ) {
            $.ajax ( {
                type: 'POST',
                url: '/india_upgrade_pos_monthly/' + get_price_of_package + '/' + pos_no + '/' + sub_type,
                success: function ( data ) {
                    $ ( "#reloading_image_gif" ).hide ()
                    razorpayPaymentScript ( data, get_price_of_package, pos_no, sub_type, "upgrade_pos_no" )
                },
                beforeSend: function () {
                    $ ( "#cancel_Addpos_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#confirm_Addpos_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#reloading_image_gif" ).show ()
                },
            } )

        }

    }
}

function upgrade_pos_confirm_order_annualy () {
    const get_price_of_package = document.getElementById ( "get_now_price_annualy" ).innerText
    const pos_no = document.getElementById ( "upgrade_pos_num_annualy" ).value;
    const span_pos_no = document.getElementById ( "pos_annualy_no" )
    const span_create_link = document.getElementById ( "span_create_link" )
    const sub_type = 'yearly'
    var function_url = ""
    if(country_code_id == "SAU" || country_code_id== "EGY"){
        function_url = "/confirm_upgrade_posNo_subscription_monthly/"

    } if(country_code_id == "TUR"){
        function_url = "/confirm_upgrade_posNo_subscription_monthly_for_turkish/"

    }
    if ( pos_no=='' || pos_no==null ) {
        const pos_unm_alert = document.getElementById ( "upgrade_pos_num_annualy" )
        pos_unm_alert.style.border = '2px solid red'
    }
    if ( pos_no!='' ) {
        if ( country_code_id!="IND" ) {
            $.ajax ( {
                type: 'POST',
                url: function_url + get_price_of_package + '/' + pos_no + '/' + sub_type,
                success: function ( data ) {
                    var data = data
                    if ( data.status=='success' ) {
                        window.location.reload ()
                    }
                    if ( data=='customer_havenot_money' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_enough_money" ).show ()
                    }
                    if ( data=='Cant_process_now' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                    if ( data=='get_code_error' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                    if ( data=='error_for_request' ) {
                        $ ( "#close-popup" ).click ()
                        $ ( "#alert_not_process" ).show ()
                    }
                },
                beforeSend: function () {
                    $ ( "#cancel_Addpos_button_annualy" ).attr ( 'disabled', 'disabled' );
                    $ ( "#confirm_Addpos_button_annualy" ).attr ( 'disabled', 'disabled' );
                    $ ( "#reloading_image_gif" ).show ()
                },
            } )
        }
        ;
        if ( country_code_id=="IND" ) {
            $.ajax ( {
                type: 'POST',
                url: '/india_upgrade_pos_monthly/' + get_price_of_package + '/' + pos_no + '/' + sub_type,
                success: function ( data ) {
                    $ ( "#reloading_image_gif" ).hide ()
                    razorpayPaymentScript ( data, get_price_of_package, pos_no, sub_type, "upgrade_pos_no" )
                },
                beforeSend: function () {
                    $ ( "#cancel_Addpos_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#confirm_Addpos_button" ).attr ( 'disabled', 'disabled' );
                    $ ( "#reloading_image_gif" ).show ()
                },
            } )
        }

    }
    ;
}

function RemovePos_button () {
    $ ( "#remove_pos_num" ).show ();
    $ ( "#subscription_button" ).hide ()
    $ ( "#AddMorePos_button" ).hide ()
    $ ( "#RemoveMorePos_button" ).hide ()
    $ ( "#cancel_Removepos_button" ).show ()
    $ ( "#confirm_Removepos_button" ).show ()
    $ ( "#current_pos_text" ).show ()
    $ ( "#links_Remove" ).show ()
};

function RemovePos_button_annualy () {
    $ ( "#remove_pos_num_annualy" ).show ();
    $ ( "#AddMorePos_button_annualy" ).hide ()
    $ ( "#RemoveMorePos_button_annualy" ).hide ()
    $ ( "#cancel_Removepos_button_annualy" ).show ()
    $ ( "#confirm_Removepos_button_annualy" ).show ()
    $ ( "#current_pos_text_annualy" ).show ()
    $ ( "#links_Remove" ).show ()
}

function upgrade_pos_confirm_order_remove () {
    const pos_no = document.getElementById ( "remove_pos_num" ).value;
    const type = 'Monthly'
    const pos_no_view = document.getElementById ( "remove_pos_num" )
    if ( pos_no=='' || pos_no==null ) {
        pos_no_view.style.border = '2px solid red'
    } else if ( pos_no!='' ) {
        $.ajax ( {
            type: 'POST',
            url: '/upgrade_pos_confirm_order_remove/' + pos_no + "/" + type,
            success: function ( data ) {
                $ ( "#message_danger_remove_pos" ).show ()
                $ ( "#cancel_Removepos_button" ).click ()
            }
        } )
    }
}

function upgrade_pos_confirm_order_remove_annualy () {
    const pos_no = document.getElementById ( "remove_pos_num_annualy" ).value;
    const type = 'yearly'
    const pos_no_view = document.getElementById ( "remove_pos_num_annualy" )
    if ( pos_no=='' || pos_no==null ) {
        pos_no_view.style.border = '2px solid red'
    } else if ( pos_no!='' ) {
        $.ajax ( {
            type: 'POST',
            url: '/upgrade_pos_confirm_order_remove/' + pos_no + "/" + type,
            success: function ( data ) {
                $ ( "#message_danger_remove_pos_annualy" ).show ()
                $ ( "#cancel_Removepos_button_annualy" ).click ()
            }
        } )
    }
}


function cancel_subscription_annualy () {
    $.ajax ( {
        type: 'POST',
        url: '/cancel_subscription_annualy',
        success: function () {
            window.location.href = '/invoices'
        }
    } )
}


function clickButtonsTest () {
    calculation_price ()
    upgrade_pos_calculation_price ()
    upgrade_pos_calculation_price_annualy ()
    calculation_price_Monthly ()
    calculation_price_annualy_subscription ()
}

function models_popup_links () {
    $ ( "#pos_text" ).hide ()
    $ ( "#pos_num_Tomonthly" ).hide ()
    $ ( "#confirm_button_monthly" ).hide ()
    $ ( "#cancel_button_monthly" ).hide ()
    $ ( "#price_text_month" ).hide ()
    $ ( "#subscription_button_monthly" ).show ()
    $ ( "#AddMorePos_button_annualy" ).show ()
    $ ( "#RemoveMorePos_button_annualy" ).show ()
    $ ( "#links_upgrade_subscription" ).hide ()
    $ ( "#upgrade_pos_num_annualy" ).hide ()
    $ ( "#Add_pos_text_annualy" ).hide ()
    $ ( "#Add_price_text_annualy" ).hide ()
    $ ( "#AddMorePos_button_annualy" ).show ()
    $ ( "#cancel_Addpos_button_annualy" ).hide ()
    $ ( "#confirm_Addpos_button_annualy" ).hide ()
    $ ( "#RemoveMorePos_button_annualy" ).show ()
    $ ( "#current_price_text_annualy" ).hide ()
    $ ( "#links_Addpos" ).hide ()
    $ ( "#remove_pos_num_annualy" ).hide ();
    $ ( "#AddMorePos_button_annualy" ).show ()
    $ ( "#RemoveMorePos_button_annualy" ).show ()
    $ ( "#cancel_Removepos_button_annualy" ).hide ()
    $ ( "#confirm_Removepos_button_annualy" ).hide ()
    $ ( "#current_pos_text_annualy" ).hide ()
    $ ( "#links_Remove" ).hide ()
    $ ( "#upgrade_pos_num" ).hide ()
    $ ( "#Add_pos_text" ).hide ()
    $ ( "#Add_price_text" ).hide ()
    $ ( "#AddMorePos_button" ).show ()
    $ ( "#cancel_Addpos_button" ).hide ()
    $ ( "#confirm_Addpos_button" ).hide ()
    $ ( "#subscription_button" ).show ()
    $ ( "#RemoveMorePos_button" ).show ()
    $ ( "#current_price_text" ).hide ()
    $ ( "#links_Addpos" ).hide ()
    $ ( "#remove_pos_num" ).hide ();
    $ ( "#subscription_button" ).show ()
    $ ( "#AddMorePos_button" ).show ()
    $ ( "#RemoveMorePos_button" ).show ()
    $ ( "#cancel_Removepos_button" ).hide ()
    $ ( "#confirm_Removepos_button" ).hide ()
    $ ( "#current_pos_text" ).hide ()
    $ ( "#links_Remove" ).hide ()
    $ ( "#current_price_text_annualy" ).hide ();
    $ ( "#pos_text" ).hide ()
    $ ( "#pos_num" ).hide ()
    $ ( "#confirm_button" ).hide ()
    $ ( "#cancel_button" ).hide ()
    $ ( "#price_text" ).hide ()
    $ ( "#subscription_button" ).show ()
    $ ( "#AddMorePos_button" ).show ()
    $ ( "#RemoveMorePos_button" ).show ()
    $ ( "#links_upgrade_subscription" ).hide ()
}

function dropdatabases_function () {
    var input, filter, table, tr;
    input = document.getElementById ( "search_with_name" );
    tr_head = document.getElementById ( "show_head" )
    filter = input.value.toUpperCase ();
    table = document.getElementById ( "invoices_table" );
    tr = table.getElementsByTagName ( "tr" );
    for (var i = 0; i < tr.length; i ++) {
        var tds = tr[ i ].getElementsByTagName ( "td" );
        var flag = ! 1;
        for (var j = 0; j < tds.length; j ++) {
            var td = tds[ j ];
            if ( td.innerHTML.toUpperCase ().indexOf ( filter ) > - 1 ) {
                flag = ! 0
            }
        }
        if ( flag ) {
            tr[ i ].style.display = "";
            tr_head.style.display = ""
        } else {
            tr[ i ].style.display = "none";
            tr_head.style.display = ""
        }
    }
};

function sameer () {
    const all_pages_data = document.getElementById ( "all_pages" );
    const table = document.getElementById ( "invoices_table" );
    const tr = table.getElementsByTagName ( "tr" );
    all_pages_data.innerText = tr.length;
    const create_ul = document.createElement ( "ul" )
    create_ul.setAttribute ( "id", 'ul_pagination' )
    const page_count = document.getElementById ( "selectRowsNum" ).value;
    for (var i = 1; i <= tr.length / page_count; i ++) {
        const create_li = document.createElement ( "li" )
        create_li.setAttribute ( "id", i )
        create_li.appendChild ( document.createTextNode ( i ) );
        create_ul.appendChild ( create_li )
        create_li.onclick = function () {
            const check_value_index = create_li.innerHTML * page_count
            const tr2 = table.getElementsByTagName ( "tr" );
            for (var s = 1; s <= tr2.length <= check_value_index; s ++) {
                if ( s >= check_value_index ) {
                    tr[ s ].style.display = "none"
                }
                if ( s <= check_value_index ) {
                    tr[ s ].style.display = ""
                }
            }
        }
    }
    document.getElementById ( "add_paginations" ).appendChild ( create_ul )
}

function change_rows_invoices () {
    sameer ()
}

sameer ()



