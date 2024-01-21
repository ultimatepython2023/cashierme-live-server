const user_id = document.getElementById( "user_id" ).value;


$( document ).ready( function () {
    upgrade_db_status()}
)

function upgrade_db_status() {
    const waitMessage = document.getElementById( "waitMessage" )
    const reg_code = document.getElementById( "reg_code" )
    const customer_password = document.getElementById( "customer_password" )
    if ( reg_code.innerText=="" ) {
        $.ajax( {
                url: '/checkDbUpdated/' + user_id,
                type: 'POST',
                async:false,
                success: function ( data ) {
                    if ( data[ "status" ]=="success" ) {
                        document.getElementById ( "db_status" ).value = "Activated";
                        waitMessage.style.display = "none"
                        $( "#LoginData" ).show()
                        $( "#registration_code" ).show()
                        customer_password.innerText = data[ "password" ]
                        reg_code.innerText = data[ "reg_code" ]
                        localStorage.setItem( "bs_name", data[ "reg_code" ] )
                        localStorage.setItem("Device",data[ "device_type" ])
                        if(data["device_type"] == "Ios"){
                            iosLisen(data["reg_code"])
                        }
                        if(data["device_type"] == "Android"){
                            androidLisen(data[ "reg_code" ])
                        }
                    }else{
                        document.getElementById ( "db_status" ).value = "pending";
                    }
                },
            }
        )
    }
}

function iosLisen(data){
    window.webkit.messageHandlers.RegistrationCode.postMessage( "" + data + "" );
}
function androidLisen(data){
    Android.showToast( "" + data+ "" );

}

function check_db_status(){
    $.ajax( {
        url: '/checkDbUpdated/'+ user_id,
        type: 'POST',
        async:false,
        success: function ( data ) {
            if(data['Result'] == "success"){
                window.location.reload()

            }

        }
    })

}


function check_account_created(){
    var reg_code = document.getElementById("reg_code").value;
    $.ajax( {
        url: '/checkAccountStatusNormal/'+ reg_code,
        type: 'POST',
        async:false,
        success: function ( data ) {
            if(data['Result'] == "Activated"){
                window.location.href='/login';
            }else if(data['Result'] == "Error"|| data['Result']=="Failed"){
                document.getElementById("waitMessage").style.display = 'none';
                document.getElementById("errorMessage").style.display = 'block';
            }

        }
    })
    
}
