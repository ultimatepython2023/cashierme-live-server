function create_subscription() {
    var name = document.getElementById ( "name" ).value;
    var email = document.getElementById ( "email" ).value;
    var password = document.getElementById ( "password" ).value;
    var business_name = document.getElementById ( "business" ).value;
    var city = document.getElementById ( "city" ).value;
    var vat_number = document.getElementById ( "vat_number" ).value;
    var commercial_register = document.getElementById ( "commercial_register" ).value;
    var country = document.getElementById ( "country" ).value;
    var postcode = document.getElementById ( "postcode" ).value;
    var street = document.getElementById ( "street" ).value;
    var phone = document.getElementById ( "phone" ).value;
    if ( name, email, password, business_name, city, vat_number
        , commercial_register, country, postcode, street, phone!="" ) {
        $ ( "#loadingss" ).show ();
    }
};


function change_status() {
    const btn_invoice = document.getElementById ( "submit_invoice" )
    if ( document.getElementById ( "check_terms" ).checked ) {
        btn_invoice.disabled = false
    } else {
        btn_invoice.disabled = true
    }
};

function calculation_price() {
    const pos_num = document.getElementById ( 'pos_num' ).value;
    const package_type = document.getElementById ( 'subtype' ).value;
    const price = document.getElementById ( 'get_price' )

    $.ajax ( {
        type: "POST",
        url: "/get_price_of_package_ofUsers/" + pos_num + '/' + package_type,
        success: function () {
        }
    } ).done ( function ( data ) {
        price.textContent = data

    } )
};

$ ( function () { // this will be called when the DOM is ready
    $ ( '#email' ).keyup ( function () {
        var datas = $ ( "#email" ).val ();
        const btn_invoice = document.getElementById ( "submit_invoice" )
        $.ajax ( {
            type: "POST",
            url: "/get_email_methods/" + datas,
            success: function () {
            }
        } ).done ( function ( data ) {
            if ( data==1 ) {
                $ ( '#email' ).css ( "background-color", "#f8d7da", )
                $ ( "#password" ).css ( "pointer-events", "none", )
                $ ( "#business" ).css ( "pointer-events", "none", )
                $ ( "#vat_number" ).css ( "pointer-events", "none", )
                $ ( "#commercial_register" ).css ( "pointer-events", "none", )
                $ ( "#phone" ).css ( "pointer-events", "none", )
                $ ( "#country" ).css ( "pointer-events", "none", )
                $ ( "#city" ).css ( "pointer-events", "none", )
                $ ( "#street" ).css ( "pointer-events", "none", )
                $ ( "#postcode" ).css ( "pointer-events", "none", )
                $ ( "#time" ).css ( "pointer-events", "none", )
                $ ( "#check_terms" ).css ( "pointer-events", "none", )
                $ ( "#alert_danger" ).show ()
            } else {
                $ ( '#email' ).css ( "background-color", '#e2f3da' )
                $ ( "#password" ).css ( "pointer-events", "auto", )
                $ ( "#business" ).css ( "pointer-events", "auto", )
                $ ( "#vat_number" ).css ( "pointer-events", "auto", )
                $ ( "#commercial_register" ).css ( "pointer-events", "auto", )
                $ ( "#phone" ).css ( "pointer-events", "auto", )
                $ ( "#country" ).css ( "pointer-events", "auto", )
                $ ( "#city" ).css ( "pointer-events", "auto", )
                $ ( "#street" ).css ( "pointer-events", "auto", )
                $ ( "#postcode" ).css ( "pointer-events", "auto", )
                $ ( "#time" ).css ( "pointer-events", "auto", )
                $ ( "#check_terms" ).css ( "pointer-events", "auto", )
                $ ( "#alert_danger" ).hide ()

            }
        } )
    } )
} );
$ ( function () {
    $ ( "#businessGetId" ).keyup ( function ( event ) {
        const add_value_url = document.getElementById ( "company_link" );
        add_value_url.innerText = this.value;
    } );
} );
function getBin(){
    var x = document.getElementById("Card_Number");
    var index = x.value.lastIndexOf(' ');
    var test = x.value.substr(index + 1);
    if (test.length === 4){
        x.value = x.value + ' ';
    }
}
function turkish_update_demo_to_enterprise(){
     var name = document.getElementById ( "name" )
    var business_string = document.getElementById ( "business_string" )
    var pos_num = document.getElementById ( "pos_num" )
    var vat_number = document.getElementById ( "vat_number" )
    var commercial_register = document.getElementById ( "commercial_register" )
    var phone = document.getElementById ( "phone" )
    var country = document.getElementById ( "country" )
    var city = document.getElementById ( "city" )
    var street = document.getElementById ( "street" )
    var sub_type = document.getElementById ('subtype').value;
     var amount = document.getElementById("paymentButtonAmount")
    var get_price = document.getElementById("get_price").innerHTML
    const recaptcha_res = document.getElementById("g-recaptcha-response").value;

    if(name.value &&  business_string.value &&
        pos_num.value && country.value && phone.value && city.value && street.value && vat_number.value && commercial_register.value&& sub_type &&recaptcha_res  != ""){
        amount.innerText = get_price
        window.location.href = "#popup1"

    }

}

function upgradeDemoToEnterpriseTurkishSubscription(){
    var name = document.getElementById ( "name" )
    var business_string = document.getElementById ( "business_string" )
    var pos_num = document.getElementById ( "pos_num" )
    var vat_number = document.getElementById ( "vat_number" )
    var commercial_register = document.getElementById ( "commercial_register" )
    var phone = document.getElementById ( "phone" )
    var country = document.getElementById ( "country" )
    var city = document.getElementById ( "city" )
    var street = document.getElementById ( "street" )
    var Card_Number= document.getElementById ('Card_Number')
    var Card_Name= document.getElementById ('Card_Name')
    var expirymonth= document.getElementById ('expirymonth')
    var expiryyear= document.getElementById ('expiryyear')
    var Card_CvC= document.getElementById ('Card_CvC')
    var alert_card_message= document.getElementById ('alert_card_message')
    var sub_type = document.getElementById ('subtype').value;
    var postcode = document.getElementById ('postcode').value;
    var imgLoader = document.getElementById("turkish_img_loader")
    var btn_submit = document.getElementById("submit_payment_btn")

    if(name.value &&  business_string.value &&
        pos_num.value && country.value && phone.value && city.value && street.value && vat_number.value && commercial_register.value && sub_type &&Card_Number.value &&Card_Name.value &&expirymonth.value &&expiryyear.value &&Card_CvC.value != ""){
         $.ajax ( {
        type: "POST",
        url: "/upgradeDemoToEnterpriseTurkishSubscription/" + name.value + '/' + business_string.value+'/'+
                                                               '/' + pos_num.value+'/'+ vat_number.value + '/' + commercial_register.value+"/"+
                                                                phone.value + '/' + country.value+"/"+ city.value + '/' + street.value+'/'+
                                                                Card_Number.value + '/' + Card_Name.value+'/'+ expirymonth.value + '/' +
                                                                 expiryyear.value+ '/' + Card_CvC.value + '/'+sub_type+'/'+postcode,
         success: function ( data ) {
            if (data['status'] == "Success"){
                imgLoader.style.display = 'none'
                window.location.href = data["URL"]
            } if (data['status'] == "Failed"){
                imgLoader.style.display = 'none'
                alert_card_message.style.display = 'block'
                alert_card_message.innerText = data['message']
                 btn_submit.style.display = ""
             }if (data['status'] == "Error"){
                imgLoader.style.display = 'none'
                Card_Number.style.border="1px solid red"
                alert_card_message.style.display = 'block'
                alert_card_message.innerText = "geçersiz kart numarası"
                 btn_submit.style.display = ""
             }if (data['status'] == "function_error"){
                imgLoader.style.display = 'none'
                alert_card_message.style.display = 'block'
                alert_card_message.innerText = "üzgünüm, şimdi işlem yapamam lütfen mektubu tekrar deneyin veya ödeme kartını değiştirin"
                 btn_submit.style.display = ""

             }
        }, beforeSend : function () {
                imgLoader.style.display = 'block'
                 btn_submit.style.display = "none"

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