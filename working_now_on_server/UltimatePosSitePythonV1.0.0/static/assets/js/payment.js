var customer_name = document.getElementById("customer_name").value;
var amount = document.getElementById("amount").value;
var order_id = document.getElementById("order_id").value;
var type = document.getElementById("type").value;


var options = {
    "key": "rzp_live_fg6d0mseHGoSRL", // Enter the Key ID generated from the Dashboard
    "amount": amount*100, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
    "currency": "INR",
    "name": customer_name,
    "description": "Cashier Me payment",
    "image": "https://cashierme.com/static/assets/img/uposNav.png",
    "order_id": order_id, //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
    "handler": function (response){
        if(type == "ES"){
            window.location.href = "/india_enterprise_subscription/" +response.razorpay_payment_id + "/"+ response.razorpay_order_id +"/"+response.razorpay_signature;
            $("#rzp-button1").hide();

            //     $.ajax({
            //     type: "POST",
            //     url: "/india_enterprise_subscription/" +response.razorpay_payment_id + "/"+ response.razorpay_order_id +"/"+response.razorpay_signature,
            //     success: function () {
            //     },  beforeSend: function () {
            //     $("#divBlockLoader").show();
            //     $("#rzp-button1").hide();
            // },
            //     }).done(function ( data ) {
            //         $("#divBlockLoader").hide();
            //         $("#rzp-button1").hide();
            //
            //
            //                       })
        }
         if(type == "UTE"){
             window.location.href="/india_upgrade_demo_to_enterprise/" +response.razorpay_payment_id + "/"+ response.razorpay_order_id +"/"+response.razorpay_signature
             $("#rzp-button1").hide();

    //              $.ajax({
    //     type: "POST",
    //     url: "/india_upgrade_demo_to_enterprise/" +response.razorpay_payment_id + "/"+ response.razorpay_order_id +"/"+response.razorpay_signature,
    //     success: function () {
    //
    //     },  beforeSend: function () {
    //             $("#divBlockLoader").show();
    //             $("#rzp-button1").hide();
    //
    //         },
    // }).done(function ( data ) {
    //     $("#divBlockLoader").hide();
    //     $("#rzp-button1").hide();
    //     window.location.href="/invoices"
    //
    // })

        }

        // alert(response.razorpay_payment_id);
        // alert(response.razorpay_order_id);
        // alert(response.razorpay_signature)
    },
    "theme": {
        "color": "#052f44"
    }
};
var rzp1 = new Razorpay(options);
rzp1.on('payment.failed', function (response){
        $.ajax({
                type: "POST",
                url: "/delete_failed_payment_order/" +order_id,
                success: function () {
                         window.location.href='/india_error_payment_message'
                }})


});
document.getElementById('rzp-button1').onclick = function(e){
    rzp1.open();
    e.preventDefault();
}