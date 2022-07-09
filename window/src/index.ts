import express, { Application } from "express";

const app: Application = express();

const port = 8000;

type Status = "OPEN" | "CLOSED" | "UNKNOWN";

app.use("/", express.static(__dirname + "/../static"));

app.get("/", (req, res) => res.redirect('/index.html'));

app.get("/status", (req, res) => {
    res.send(windowStatus)
});
function get(subscription:string){
    return {
        humidity: 10,
        temperature: 50,
        uv: 400
    }
}
let windowStatus:Status = "UNKNOWN";

function subscriber(){
    const value = get("/data");
    if ((value.temperature > 25 || value.humidity > 10 ) && value.uv<200){
        windowStatus = "OPEN";
    }else{
        windowStatus = "CLOSED"
    }
    setTimeout(subscriber, 5000);
}

app.listen(port, () => {
    console.log(`Connected successfully on port ${port}`);
});
