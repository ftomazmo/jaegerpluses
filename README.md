Build the images (only if you are me, otherwise jump to the next step. This images are already available publicly)
```sh
docker build -f ./otel-flask/Dockerfile --push -t ftomazmo/otel-flask ./otel-flask
docker build -f ./otel-node/Dockerfile --push -t ftomazmo/otel-node ./otel-node
```
Create local k8s cluster using [kind](https://kind.sigs.k8s.io)
```sh
kind create cluster
```
Apply deployments and services on cluster
```sh
kubectl --context kind-kind apply -f local.yml
```
Foward the ports to access the applications
```sh
kubectl port-forward --context kind-kind -n development svc/jaeger-web 16686:16686
kubectl port-forward --context kind-kind -n development svc/flask-web 5000:5000
kubectl port-forward --context kind-kind -n development svc/nodejs-web 8080:8080
```
Generate trific on apps
```sh
curl http://localhost:5000
curl http://localhost:8080/rolldice
```
Check traces on Jaeger on browser [http://localhost:16686](http://localhost:16686)

To clean up your environment:
```sh
kind delete clusters kind
```
