function submit_end_email() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const subject = document.getElementById("subject").value;
    const message = document.getElementById("message").value;
    const recaptcha_res = document.getElementById("g-recaptcha-response").value;

    if (recaptcha_res != ''){
        $.ajax({
            type: "POST",
            url: "/send_email/"+ name +"/"+ email+ "/"+ subject + "/" + message ,
            success: function(data) {
                if(data == "ok"){
                    $("#success_send").show()
                    $("#name").val("")
                    $("#email").val("")
                    $("#subject").val("")
                    $("#message").val("")
                } if(data == "failed"){
                    $("#failed_send").show()
                    $("#success_send").show()
                    $("#name").val("")
                    $("#email").val("")
                    $("#subject").val("")
                    $("#message").val("")
                }
            },
            beforeSend: function () {
                $("#dasdadadfdsfdsfsdf").show();
            },
            complete: function () {
                $("#dasdadadfdsfdsfsdf").hide();
            }})


    }


};

var country = document.getElementById("checkCountry").value;


if(country == "TUR"){
    var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();
    (function(){
       var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
       s1.async=true;
       s1.src='https://embed.tawk.to/6304956554f06e12d8903809/1gb4uf59b';
       s1.charset='UTF-8';
       s1.setAttribute('crossorigin','*');
       s0.parentNode.insertBefore(s1,s0);
}if(country == "SAU" || country == "EGY"){
    var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();
    (function(){
        var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
        s1.async=true;
        s1.src='https://embed.tawk.to/61f4637db9e4e21181bc71dc/1fqha9bq0';
        s1.charset='UTF-8';
        s1.setAttribute('crossorigin','*');
        s0.parentNode.insertBefore(s1,s0);
    })();
}if(country == "IND"|| country == "MYS" || country == "GLB"){
    var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();
    (function(){
        var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
        s1.async=true;
        s1.src='https://embed.tawk.to/62ab09af7b967b117994dbe1/1g5m1rm93';
        s1.charset='UTF-8';
        s1.setAttribute('crossorigin','*');
        s0.parentNode.insertBefore(s1,s0);
    })();

}

//
// if(country != "IND"|| country != "MYS"||country != "TUR" || country != "SAU" || country !="EGY"){
//     var Tawk_API=Tawk_API||{}, Tawk_LoadStart=new Date();
//     (function(){
//         var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
//         s1.async=true;
//         s1.src='https://embed.tawk.to/62ab09af7b967b117994dbe1/1g5m1rm93';
//         s1.charset='UTF-8';
//         s1.setAttribute('crossorigin','*');
//         s0.parentNode.insertBefore(s1,s0);
//     })();
//
// }






$(function(){
    $("#businessGetId").keyup(function(event){
        const add_value_url = document.getElementById("company_link");
        add_value_url.innerText = this.value;

    });
});