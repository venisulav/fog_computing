import express, { Application } from "express";

import axios from "axios";

const app: Application = express();

const edge_broker = "http://localhost:5002";

const port = 8000;

type Status = object;

app.use("/", express.static(__dirname + "/../static"));

app.get("/", (req, res) => res.redirect('/index.html'));

app.get("/status", (req, res) => {
    res.send(windowStatus)
});
async function getNewStatus(){
    try{
       const response =  await axios.get(edge_broker+"/sensorTargets");
       if (response.status == 200){
           windowStatus = response.data;
           console.log("New status from broker:",windowStatus);
       }else if(response.status == 404/**empty queue*/){
           console.log("Queue is empty")
       }else{
           console.log("HTTP: error:",response.status);
       }
    }catch(error){
        console.log("Error",error)
    }
}
let windowStatus:Status = {};

async function subscriber(){
    await getNewStatus();
    setTimeout(subscriber, 3000);
}
subscriber();

app.listen(port, () => {
    console.log(`Connected successfully on port ${port}`);
});
