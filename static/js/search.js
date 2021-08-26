const h2 = document.querySelector('.login h2');
const p = document.querySelector('.login p');
const successParagraph = document.querySelector('.success');
const errorParagraph = document.querySelector('.error');

if (successParagraph || errorParagraph) {
   h2.style.marginTop = '0%';
   p.style.marginTop = '0%';
}