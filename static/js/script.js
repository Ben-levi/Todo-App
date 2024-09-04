
// for (i=0; i < allInputs.length; i++ ) {
//     allInputs[i].addEventListener("focus", () => {
//         //search for the lable related to this input
//         const lable = document.querySelector();
//         lable.style.fontWeight = "bold";
        
//     })
// }

document.querySelectorAll('input, select').forEach(input => {
    const label = input.closest('div').querySelector('label');
    
    input.addEventListener('focus', () => {
        label.style.fontWeight = 'bold';
        input.style.color = 'black';
    });
    
    input.addEventListener('blur', () => {
        label.style.fontWeight = 'normal';
        input.style.color = 'green';
    });
});
