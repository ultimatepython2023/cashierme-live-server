function remove_qutations_and_tags(){
    var validation_name = document.getElementById("name")
    var result = validation_name.value.replace(/['"@#$^&*_+]+/g, '')
    validation_name.value = result
}

$(function(){ // this will be called when the DOM is ready
    $('#email').keyup(function() {
        var datas = $("#email").val();
        var btn_invoice = document.getElementById("submit_button")
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
    $('#contact_number').keyup(function() {
        var get_phone =  document.getElementById("contact_number").value;
        var btn_invoice = document.getElementById("submit_button")

        $.ajax({
            type: "POST",
            url: "/get_email_methods/"+ get_phone+"/"+"contact",
            success: function () {
            }
        }).done(function(data){
            if (data == 1){
                document.getElementById("contact_number").style.backgroundColor = "#f8d7da"
                document.getElementById("contact_number_validation").style.display = ""
                btn_invoice.disabled = true;
            }
            else{
                document.getElementById("contact_number").style.backgroundColor = "#e2f3da"
                document.getElementById("contact_number_validation").style.display = "none"
                btn_invoice.disabled = false


            }
        })
    })
});


$(function(){
    $("#businessGetId").keyup(function(event){
        const add_value_url = document.getElementById("company_link");
        const submit_subscription_demo = document.getElementById("submit_button")
        const validation_company_id = document.getElementById("validation_company_id");


        if(this.value.length < 3){
            this.style.border='2px solid red'
            submit_subscription_demo.disabled = true
            validation_company_id.style.display = 'block'

        }
        else{
            this.style.border='1px solid #ced4da'
            submit_subscription_demo.disabled = false
            validation_company_id.style.display = 'none'

        }
        add_value_url.innerText = this.value;
    });
});


$(function(){
    $("#name").keyup(function(event){
        const add_value_url = document.getElementById("validation_name");
        const name = document.getElementById("name").value;
        const submit_subscription_demo = document.getElementById("submit_button")
        if(name.length <3 ){
            add_value_url.style.display = 'block'
            this.style.border='1px solid red'
            submit_subscription_demo.disabled = true
        }
        if(name.length >=3 ){
            add_value_url.style.display = 'none'
            this.style.border='1px solid #ced4da'
            submit_subscription_demo.disabled = false

        }
    });
});

$(function(){
    $("#password").keyup(function(event){
        const add_value_url = document.getElementById("validation_password");
        const password = document.getElementById("password").value;
        const submit_subscription_demo = document.getElementById("submit_button")

        // var passw=  /^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{7,15}$/;
        if(password.length > 7 && password.match(/(?=.*[a-zA-Z]).{7,}/)){
            add_value_url.style.display = 'none'
            this.style.border='1px solid #ced4da'
            submit_subscription_demo.disabled = false

        }
        else{
            add_value_url.style.display = 'block'
            this.style.border='1px solid red'
            submit_subscription_demo.disabled = true

        }


    });
});

$(function(){
    $("#business_string").keyup(function(event){
        const add_value_url = document.getElementById("validation_company");
        const company_string = document.getElementById("business_string").value;
        const submit_subscription_demo = document.getElementById("submit_button")

        if(company_string.length < 3  ){
            add_value_url.style.display = 'block'
            this.style.border='1px solid red'
            submit_subscription_demo.disabled = true

        }
        if(company_string.length >= 3 ){
            add_value_url.style.display = 'none'
            this.style.border='1px solid #ced4da'
            submit_subscription_demo.disabled = false

        }

    });
});

       function removeSpaces() {
        var businessGetId = document.getElementById("businessGetId").value;
        var business = document.getElementById("businessGetId")
        var link = document.getElementById("company_link")
        business.value =businessGetId.replace(/\s+/g, '');
        link.innerText = businessGetId.replace(/\s+/g, '');
    }
