import express, { Application } from "express";

import axios from "axios";

const app: Application = express();

const PORT = process.env.PORT;
const HOST = process.env.HOST;
// const EDGE_BROKER = process.env.EDGE_BROKER;
const EDGE_BROKER = "127.0.0.1:5002";

console.log(`EDGE_BROKER:${EDGE_BROKER}`)

type Status = object;

app.use("/", express.static(__dirname + "/../static"));

app.get("/", (req, res) => res.redirect('/index.html'));

app.get("/status", (req, res) => {
    res.send(windowStatus)
});
async function readDirectlyFromSensor(){
    console.log("Fetching from the Sensor Queue");
    try{
        const response =  await axios.get("http://"+EDGE_BROKER+"/sensorQueue");
        if (response.status == 200){
            windowStatus = response.data;
            console.log("New status from broker's sensor queue:",windowStatus);
        }else{
            console.log("Unexpected response code:",response.status);
        }
     }catch(error:any){
        if (error.response){
            if (error.response.status === 404){
                console.log("Sensor Queue is empty!");
            }
        }else if(error.request){
            console.error("Error. Cannot connect to edge broker!")
        }else{
            console.error("Unknown Error:", error.message)
        }
     }
}
async function getNewStatus(){
    try{
       const response =  await axios.get("http://"+EDGE_BROKER+"/processedQueue");
       if (response.status == 200){
           windowStatus = response.data;
           console.log("New status from broker's processed queue:",windowStatus);
       }else{
           console.log("Unexpected response code:",response.status);
       }
    }catch(error:any){
        if (error.response){
            if (error.response.status === 404){
                console.log("Processed Queue is empty");
                await new Promise(r => setTimeout(r, 10000));
                readDirectlyFromSensor();
            }
        }else if(error.request){
            console.error("Error. Cannot connect to edge broker!");
        }else{
            console.error("Unknown Error:", error.message)
        }
    }
}
let windowStatus:Status = {};

async function subscriber(){
    await getNewStatus();
    setTimeout(subscriber, 5000);
}
subscriber();

app.listen(PORT, () => {
    console.log(`Connected successfully on port ${PORT}`);
});
