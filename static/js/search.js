const h2 = document.querySelector('.login h2');
const p = document.querySelector('.login p');
const successParagraph = document.querySelector('.success');
const errorParagraph = document.querySelector('.error');
const details = document.querySelector('#address-list');
const formInput = document.querySelector('#street_address');
const form = document.querySelector('form');
const bottomSvg = document.querySelector('.bottom');
const spinner = document.querySelector('.spinner-div');

// set styling if a success or error message appears
// so as not to push content too far down on page
if (successParagraph || errorParagraph) {
   h2.style.marginTop = '0%';
   p.style.marginTop = '0%';
}

// manipulate the value of the bottom SVG's div
// so that it will be appropriately spaced on the page
// depending on the results of the autocomplete api calls
const makeSpaceForAutoComplete = () => {
   if (formInput.value === '') {
      bottomSvg.style.bottom = '0'
   } else {
      bottomSvg.style.bottom = '-150px'
   }
   if (window.innerWidth < 900) {
      bottomSvg.style.bottom = '0'
   }
}

// gets the details from the autocomplete api and
// adds them to the DOM
const getDetails = arr => {
   // if we get an empty result set, reset the height of
   // the bottom SVG and return
   if (!arr.length) {
      bottomSvg.style.bottom = '0';
      details.innerHTML = '';
      return;
   }

   // clear the autocomplete details div, 
   // perform string manipulation on each member
   // of the array, and add it to the autocomplete div
   details.innerHTML = '';
   let regex = /(NW)|(SE)|(SW)|(NE)/;
   arr.forEach((el, idx) => {
       let newDiv = document.createElement('div');
       let label = el.label.split(',').reverse().join(', ').replace(regex, '');
       newDiv.innerText = label;
       newDiv.id = `choice${idx}`
       newDiv.classList.add('choice');
       details.append(newDiv)
       details.style.display = 'block'
   })

   if (window.innerWidth > 900) {
      bottomSvg.style.bottom = '-150px'
   }
}

// if the user selects a choice from the autocomplete
// dropdown, fill it into the form input, reset appropriate
// styles, and submit the form.
const fillInInput = (evt) => {
   formInput.value = evt.target.innerText;
   details.style.display = 'none';
   bottomSvg.style.bottom = '0';
   form.submit();
   form.style.display = 'none';
   spinner.style.display = 'flex';
}


// set up the DOM style-wise to handle the new autocomplete div,
// call the api and get results, then add those results to the DOM
// with "getDetails".
async function makeAutoComplete() {
   details.style.display = formInput.value === '' ? 'none' : 'block';
   makeSpaceForAutoComplete();
   let config = {
       params: {
           apiKey: 'wkGs3Y1XsWBHM9nmv085V2IcnO6Kez1bgRd8kYrIiw4',
           query: formInput.value
       }
   }
   let res = await axios.get('https://autocomplete.geocoder.ls.hereapi.com/6.2/suggest.json', config);
   let [...places] = res.data.suggestions
   getDetails(places);
   
}

// Makes it so that the api is not called every time 
// the user makes a keystroke
const debounce = (func) => {
   let timer;
   return () => {
       clearTimeout(timer);
       timer = setTimeout(() => (func()),300);
   }
}

formInput.addEventListener('input', debounce(makeAutoComplete));
details.addEventListener('click', fillInInput);