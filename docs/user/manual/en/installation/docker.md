# Installing and Running ERPNext using Docker

This guide provides detailed instructions on how to install and run ERPNext using Docker.

## Prerequisites

Before you begin, ensure that you have Docker installed on your system. You can find the installation instructions for your operating system on the [Docker website](https://docs.docker.com/get-docker/).

## Steps to Install and Run ERPNext

1. **Pull the ERPNext Docker image**

   Open a terminal and run the following command to pull the ERPNext Docker image from Docker Hub:

   ```sh
   docker pull frappe/erpnext
   ```

2. **Create a Docker network**

   Create a Docker network for ERPNext by running the following command:

   ```sh
   docker network create erpnext-network
   ```

3. **Start the ERPNext container**

   Start the ERPNext container by running the following command:

   ```sh
   docker run -d --name erpnext --network erpnext-network -p 80:80 frappe/erpnext
   ```

4. **Access ERPNext**

   Open your web browser and navigate to `http://localhost` to access ERPNext.

## Additional Configuration

You can customize the ERPNext Docker container by using environment variables and mounting volumes. Refer to the [ERPNext Docker documentation](https://github.com/frappe/frappe_docker) for more details on advanced configuration options.
