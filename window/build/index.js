"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const app = (0, express_1.default)();
const port = 8000;
app.use("/", express_1.default.static(__dirname + "/../static"));
app.get("/", (req, res) => res.redirect('/index.html'));
app.get("/status", (req, res) => {
    res.send(windowStatus);
});
function get(subscription) {
    return {
        humidity: 10,
        temperature: 50,
        uv: 400
    };
}
let windowStatus = "UNKNOWN";
function subscriber() {
    const value = get("/data");
    if ((value.temperature > 25 || value.humidity > 10) && value.uv < 200) {
        windowStatus = "OPEN";
    }
    else {
        windowStatus = "CLOSED";
    }
    setTimeout(subscriber, 5000);
}
app.listen(port, () => {
    console.log(`Connected successfully on port ${port}`);
});
