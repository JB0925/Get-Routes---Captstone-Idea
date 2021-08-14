class Navbar {
    constructor() {
        this.ul = document.querySelector('nav ul');
        this.burgerMenu = document.querySelector('#burger');
        this.pullDown = document.querySelector('.pulldown');
        this.pullDownH2 = document.querySelectorAll('.pulldown h2');
        this.pullDownButton = document.querySelector('.pulldown button');
        this.toggleMenu = false;
        this.handleClick = this.handleClick.bind(this);
        this.handleScreenWidth = this.handleScreenWidth.bind(this);
    }

    handleScreenWidth() {
        if (window.innerWidth >= 900) {
            setTimeout(() => {
                this.pullDown.style.height = "0px";
                this.pullDown.style.marginBottom = "0%";
                this.pullDownButton.style.display = "none";
                this.pullDownButton.style.opacity = "1"
                for (let p of this.pullDownH2) {
                    p.style.display = "none"
                    p.style.opacity = "1"
                }
            },100);
            this.toggleMenu = false;
        }
    }

    handleClick(evt) {
        if (!this.toggleMenu) {
            setTimeout(() => {
                this.pullDown.style.height = "250px";
                this.pullDown.style.marginBottom = "3%";
                this.pullDownButton.style.display = "block";
                this.pullDownButton.style.opacity = "1";
                for (let p of this.pullDownH2) {
                    p.style.display = "block"
                    p.style.opacity = "1"
                }
            },100);
            this.toggleMenu = true;
        } else {
            setTimeout(() => {
                this.pullDown.style.height = "0px";
                this.pullDown.style.marginBottom = "0%";
                this.pullDownButton.style.display = "none";
                this.pullDownButton.style.opacity = "1"
                for (let p of this.pullDownH2) {
                    p.style.display = "none"
                    p.style.opacity = "1"
                }
            },100);
            this.toggleMenu = false;
        };
    };

    
};

n = new Navbar()
n.burgerMenu.addEventListener('click', n.handleClick)
window.addEventListener('resize', n.handleScreenWidth)