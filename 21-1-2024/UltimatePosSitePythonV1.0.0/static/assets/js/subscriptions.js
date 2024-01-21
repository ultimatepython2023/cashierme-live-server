$(document).ready(function(){
    var r = document.querySelector(':root');
    var userLan = document.getElementById("get_currentuser_lang").value;
    if(userLan == 'en' || userLan == "tr" || userLan == "gl"){

        r.style.setProperty('--mainDir', 'ltr');

    }else{
        r.style.setProperty('--mainDir', 'rtl');
    }
});
$(document).ready(function(){
    var owl = $('.owl-carousel.pricing');
    if (owl) {
        var userLan = document.getElementById("get_currentuser_lang").value;
        var result ;
        if(userLan == 'en' || userLan == "tr" || userLan == "gl"){
            result = false
        }else{
            result = true
        }
        setTimeout(function () {
            owl.owlCarousel({
                rtl:result,
                stagePadding: 100,
                loop:true,
                margin:30,
                nav:false,
                responsive:{
                    0:{
                        items:1,
                        stagePadding: 40,
                    },
                    600:{
                        items:3,
                        stagePadding: 100,
                    },
                }
            });
        }, 500);
    }
});
function create_subscription() {
    var name = document.getElementById("name").value;
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    var business_name = document.getElementById("business").value;
    var city = document.getElementById("city").value;
    var vat_number = document.getElementById("vat_number").value;
    var commercial_register = document.getElementById("commercial_register").value;
    var country = document.getElementById("country").value;
    var postcode = document.getElementById("postcode").value;
    var street = document.getElementById("street").value;
    var phone = document.getElementById("phone").value;
    if (name, email, password, business_name, city, vat_number, commercial_register, country, postcode, street, phone != "") {
        $("#loadingss").show()
    }
};

function change_status() {
    const btn_invoice = document.getElementById("submit_invoice")
    if (document.getElementById("check_terms").checked) {
        btn_invoice.disabled = ! 1
    } else {
        btn_invoice.disabled = ! 0
    }
};

function calculation_price() {
    const pos_num = document.getElementById('pos_num').value;
    const package_type = document.getElementById('subtype').value;
    const price = document.getElementById('get_price')
    $.ajax({
        type: "POST",
        url: "/get_price_of_package_ofUsers/" + pos_num + '/' + package_type,
        success: function () {
        }
    }).done(function ( data ) {
        price.textContent = data
    })
};

$(function(){ // this will be called when the DOM is ready
    $('#email').keyup(function() {
        var datas = $("#email").val();
        var btn_invoice = document.getElementById("submit_invoice")
        $.ajax({
            type: "POST",
            url: "/get_email_methods/"+ datas+"/"+"email",
            success: function () {
            }
        }).done(function(data){
            if (data == 1){
                $('#email').css("background-color", "#f8d7da",)
                $("#alert_danger").show()
                btn_invoice.disabled = true;

            }
            else{
                $('#email').css("background-color", '#e2f3da')
                $("#alert_danger").hide()
                btn_invoice.disabled = false

            }
        })
    })
});

$(function(){ // this will be called when the DOM is ready
    $('#phone').keyup(function() {
        var get_phone =  document.getElementById("phone").value;
        var btn_invoice = document.getElementById("submit_invoice")

        $.ajax({
            type: "POST",
            url: "/get_email_methods/"+ get_phone+"/"+"contact",
            success: function () {
            }
        }).done(function(data){
            if (data == 1){

                document.getElementById("phone").style.backgroundColor = "#f8d7da"
                document.getElementById("contact_number_validation").style.display = ""
                btn_invoice.disabled = true;
            }
            else{
                document.getElementById("phone").style.backgroundColor = "#e2f3da"
                document.getElementById("contact_number_validation").style.display = "none"

                btn_invoice.disabled = false


            }
        })
    })
});




$(function () {
    $("#businessGetId").keyup(function ( event ) {
        const add_value_url = document.getElementById("company_link");
        const validation_company_id = document.getElementById("validation_company_id");
        if (this.value.length < 3) {
            this.style.border = '2px solid red'
            validation_company_id.style.display = 'block'
        } else {
            this.style.border = '1px solid #ced4da'
            validation_company_id.style.display = 'none'
        }
        add_value_url.innerText = this.value
    })
});
$(function () {
    $("#name").keyup(function ( event ) {
        const add_value_url = document.getElementById("validation_name");
        const name = document.getElementById("name").value;
        if (name.length < 3) {
            add_value_url.style.display = 'block'
            this.style.border = '1px solid red'
        }
        if (name.length >= 3 ) {
            add_value_url.style.display = 'none'
            this.style.border = '1px solid #ced4da'
        }
    })
});
$(function () {
    $("#password").keyup(function ( event ) {
        const add_value_url = document.getElementById("validation_password");
        const password = document.getElementById("password").value;
        if(password.length > 7 && password.match(/(?=.*[a-zA-Z]).{7,}/)){
            add_value_url.style.display = 'none'
            this.style.border = '1px solid #ced4da'
        } else {
            add_value_url.style.display = 'block'
            this.style.border = '1px solid red'
        }
    })
});
$(function () {
    $("#business_string").keyup(function ( event ) {
        const add_value_url = document.getElementById("validation_company");
        const company_string = document.getElementById("business_string").value;
        if (company_string.length < 3) {
            add_value_url.style.display = 'block'
            this.style.border = '1px solid red'
        }
        if (company_string.length >= 3) {
            add_value_url.style.display = 'none'
            this.style.border = '1px solid #ced4da'
        }
    })
})


       function removeSpaces() {
        var businessGetId = document.getElementById("businessGetId").value;
        var business = document.getElementById("businessGetId")
        var link = document.getElementById("company_link")
        business.value =businessGetId.replace(/\s+/g, '');
        link.innerText = businessGetId.replace(/\s+/g, '');
    }