document.getElementById('id_acc_dr').addEventListener("click", function(event) {
    event.preventDefault();
    let account_selector = document.getElementById('account-selector')
    account_selector.style.display = "block";
    this.blur();
    account_selector.focus()
    document.getElementById('acc_type').value = 'dr';
})

document.getElementById('id_acc_cr').addEventListener("click", function(event) {
    event.preventDefault();
    let account_selector = document.getElementById('account-selector')
    account_selector.style.display = "block";
    this.blur();
    account_selector.focus()
    document.getElementById('acc_type').value = 'cr';
})

document.getElementById('account-selector').addEventListener('click', function(event){
    document.getElementById('account-selector').style.display = 'none';
})

let accItems = document.getElementsByClassName('acc-item')
for(let i = 0; i < accItems.length; i++) {
    accItems[i].addEventListener("click", function(event) {
        // console.log("Clicked index: " + i);
        let account_selector = document.getElementById('account-selector')
        let accPk = event.target.dataset.accpk
        let acc_type = document.getElementById('acc_type').value
        if (acc_type == 'dr') {
            document.getElementById('id_acc_dr').value = accPk;
        }
        else {
            document.getElementById('id_acc_cr').value = accPk;
        }
        // account_selector.style.display = "none";
    })
}