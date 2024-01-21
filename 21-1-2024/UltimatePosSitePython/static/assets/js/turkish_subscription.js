function getBin() {
    var x = document.getElementById("Card_Number");
    var index = x.value.lastIndexOf(' ');
    var test = x.value.substr(index + 1);
    if (test.length === 4) {
        x.value = x.value + ' ';
    }
}
function remove_qutations_and_tags(){
    var validation_name = document.getElementById("name")
    var result = validation_name.value.replace(/['"@#$^&*_+]+/g, '')
    validation_name.value = result
}



function create_turkish_enterprise_subscription(){
     var name = document.getElementById ( "name" )
    var email = document.getElementById ( "email" )
    var password = document.getElementById ( "password" )
    var business_string = document.getElementById ( "business_string" )
    var businessGetId = document.getElementById ( "businessGetId" )
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


    if(name.value && email.value && password.value && business_string.value && businessGetId.value &&
        pos_num.value && country.value && phone.value && city.value && street.value && vat_number.value && commercial_register.value&& sub_type&&recaptcha_res   != ""){
        amount.innerText = get_price
        window.location.href = "#popup1"

    }

}

function createEnterpriseSubscriptionTurkish(){
    var name = document.getElementById ( "name" )
    var email = document.getElementById ( "email" )
    var password = document.getElementById ( "password" )
    var business_string = document.getElementById ( "business_string" )
    var businessGetId = document.getElementById ( "businessGetId" )
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
    if(name.value && email.value && password.value && business_string.value && businessGetId.value &&
        pos_num.value && country.value && phone.value && city.value && street.value && vat_number.value && commercial_register.value && sub_type &&Card_Number.value &&Card_Name.value &&expirymonth.value &&expiryyear.value &&Card_CvC.value != ""){
         $.ajax ( {
        type: "POST",
        url: "/create_turkish_enterprise_subscription_live/" + name.value + '/' + email.value +'/'+
                                                               password.value + '/' + business_string.value+'/' + businessGetId.value +
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
                alert_card_message.style.display = ''
                alert_card_message.innerText = data["message"]
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
