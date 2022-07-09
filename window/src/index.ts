import express, { Application } from "express";

import axios from "axios";

const app: Application = express();

const PORT = process.env.PORT;
const HOST = process.env.HOST;
const EDGE_BROKER = process.env.EDGE_BROKER;

console.log(`EDGE_BROKER:${EDGE_BROKER}`)

type Status = object;

app.use("/", express.static(__dirname + "/../static"));

app.get("/", (req, res) => res.redirect('/index.html'));

app.get("/status", (req, res) => {
    res.send(windowStatus)
});
async function getNewStatus(){
    try{
       const response =  await axios.get("http://"+EDGE_BROKER+"/sensorTargets");
       if (response.status == 200){
           windowStatus = response.data;
           console.log("New status from broker:",windowStatus);
       }else if(response.status == 404/**empty queue*/){
           console.log("Queue is empty")
       }else{
           console.log("HTTP: error:",response.status);
       }
    }catch(error:any){
        console.log("Error",error.message)
    }
}
let windowStatus:Status = {};

async function subscriber(){
    await getNewStatus();
    setTimeout(subscriber, 3000);
}
subscriber();

app.listen(PORT, () => {
    console.log(`Connected successfully on port ${PORT}`);
});
