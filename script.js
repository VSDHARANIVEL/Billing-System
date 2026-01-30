const API = "http://127.0.0.1:5000";

function fetchProduct() {
    let code = document.getElementById("code").value;

    if (code.length === 3) {
        fetch(API + "/get_product/" + code)
        .then(res => res.json())
        .then(data => {
            if (!data.error) {
                productInfo.innerHTML =
                    "Product: " + data.name +
                    "<br>Price: ₹" + data.price +
                    "<br>Stock: " + data.stock;
            } else {
                productInfo.innerHTML = "Invalid Product Code";
            }
        });
    }
}

function generateBill() {
    fetch(API + "/generate_bill", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            phone: phone.value,
            worker: worker.value,
            code: code.value,
            quantity: quantity.value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(
                "Bill Generated\n" +
                "Total Amount: ₹" + data.total +
                "\nWorker Incentive: ₹" + data.incentive
            );
        }
    });
}
