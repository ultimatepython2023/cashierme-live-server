! function () {
    "use strict";
    const e = (e, t = ! 1) => ( e = e.trim(), t ? [...document.querySelectorAll(e)] : document.querySelector(e) ),
        t = (t, o, s, i = ! 1) => {
            let a = e(o, i);
            a && ( i ? a.forEach(e => e.addEventListener(t, s)) : a.addEventListener(t, s) )
        }, o = (e, t) => {
            e.addEventListener("scroll", t)
        };
    let s = e("#navbar .scrollto", ! 0);
    const i = () => {
        let t = window.scrollY + 200;
        s.forEach(o => {
            if (! o.hash) return;
            let s = e(o.hash);
            s && ( t >= s.offsetTop && t <= s.offsetTop + s.offsetHeight ? o.classList.add("active") : o.classList.remove("active") )
        })
    };
    window.addEventListener("load", i), o(document, i);
    const a = t => {
        let o = e("#header"), s = o.offsetHeight;
        o.classList.contains("header-scrolled") || ( s -= 20 );
        let i = e(t).offsetTop;
        window.scrollTo({top: i - s, behavior: "smooth"})
    };
    let l = e("#header");
    if (l) {
        const e = () => {
            window.scrollY > 100 ? l.classList.add("header-scrolled") : l.classList.remove("header-scrolled")
        };
        window.addEventListener("load", e), o(document, e)
    }
    let n = e(".back-to-top");
    if (n) {
        const e = () => {
            window.scrollY > 100 ? n.classList.add("active") : n.classList.remove("active")
        };
        window.addEventListener("load", e), o(document, e)
    }
    t("click", ".mobile-nav-toggle", function (t) {
        e("#navbar").classList.toggle("navbar-mobile"), this.classList.toggle("bi-list"), this.classList.toggle("bi-x")
    }), t("click", ".navbar .dropdown > a", function (t) {
        e("#navbar").classList.contains("navbar-mobile") && ( t.preventDefault(), this.nextElementSibling.classList.toggle("dropdown-active") )
    }, ! 0), t("click", ".scrollto", function (t) {
        if (e(this.hash)) {
            t.preventDefault();
            let o = e("#navbar");
            if (o.classList.contains("navbar-mobile")) {
                o.classList.remove("navbar-mobile");
                let t = e(".mobile-nav-toggle");
                t.classList.toggle("bi-list"), t.classList.toggle("bi-x")
            }
            a(this.hash)
        }
    }, ! 0), window.addEventListener("load", () => {
        window.location.hash && e(window.location.hash) && a(window.location.hash)
    });
    let c = e("#preloader");
    c && window.addEventListener("load", () => {
        c.remove()
    });
    GLightbox({selector: ".gallery-lightbox"});
    new Swiper(".testimonials-slider", {
        speed: 600,
        loop: ! 0,
        autoplay: {delay: 5e3, disableOnInteraction: ! 1},
        slidesPerView: "auto",
        pagination: {el: ".swiper-pagination", type: "bullets", clickable: ! 0}
    }), window.addEventListener("load", () => {
        AOS.init({duration: 1e3, easing: "ease-in-out", once: ! 0, mirror: ! 1})
    })
}()