var buttonRecord = document.getElementById("record");
var buttonStop = document.getElementById("stop");


buttonRecord.onclick = function() {
    // var url = window.location.href + "record_status";

    
    // disable download link
    var downloadLink = document.getElementById("download");


    // XMLHttpRequest
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            // alert(xhr.responseText);
        }
    }
    xhr.open("POST", "/captureimage");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ status: "true" }));
};
