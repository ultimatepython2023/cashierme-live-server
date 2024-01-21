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