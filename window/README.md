# running a dev server
```
npm install
npm run start
```

This spins up local server and it gets updated automatically when sources change.

# build and run the container
```
npm run build
docker build --tag window-manager .
docker run -p 8000:8000 -it window-manager
```
