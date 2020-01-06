# Elektrum Network

The scripts in the `network` subdirectory of the project configure a VPC network and database instance on AWS for use by the Elektrum app.

## Usage

* Place the Ansible vault passphrase in a file named `[env]-vault-password.txt` in the `environments` directory. Password should be by itself on one line.
* Execute `run.sh [development|staging|production]` to run the playbook in order to configure the network components for a given environment.

## Architecture

```
                                                    ┌─────────────┐
                                                    │     DNS     │
                                                    │  (Route53)  │
                                                    ├─────────────┤
                                                    │     CDN     │
                                                    │(Cloudfront) │
                                                    └─────────────┘
                                                           ▲
                                                           │
                   ┌────────────────────────────────────┬─────┬──────────────────────────────────┐
                   │                                    │ IGW │                                  │
                   │    ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐ └─────┘┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─     │
                   │                                       ▲                                │    │
                   │ ┌──┼─────────────────────────────┼────┼───┼───────────────────────────────┐ │
                   │ │                                     │                                │  │ │
                   │ │  │  ┌──────────────────────┐   │┌──────┐│   ┌──────────────────────┐    │ │
                   │ │     │  ┌─────────────┬──┐  │    │router│    │  ┌──┬──────────────┐ │ │  │ │
                   │ │  │  │  │     NAT     │E │  │   │└──────┘│   │  │E │     NAT      │ │    │ │
                   │ │     │  │   Instance  │I │◀─┼┐       ▲      ┌┼─▶│I │   Instance   │ │ │  │ │
                   │ │  │  │  │    [EC2]    │P │  ││  │    │   │  ││  │P │    [EC2]     │ │    │ │
  public-01 subnet─┼─┼────▶│  └─────────────┴──┘  │└───────┼──────┘│  └──┴──────────────┘ │◀┼──┼─┼─public-02 subnet
                   │ │  │  └──────────────────────┘   │    │   │   └──────────────────────┘    │ │
                   │ │     ┌──────────────────────┐        │       ┌──────────────────────┐ │  │ │
                   │ │  │  │ ┌──────────────┬──┐  │   │    │   │   │  ┌──┬──────────────┐ │    │ │
                   │ │     │ │ elektrum_app │E │  │        │       │  │E │ elektrum_app │ │ │  │ │
private-01 subnet ─┼─┼──┼─▶│ │   [Lambda]   │N │◀─┼───┼────┴───┼───┼─▶│N │   [Lambda]   │ │◀───┼─┼─private-02 subnet
                   │ │     │ │              │I │  │                │  │I │              │ │ │  │ │
                   │ │  │  │ └──────────────┴──┘  │   │        │   │  └──┴──────────────┘ │    │ │
                   │ │     └─────────┬────────────┘                └─────────────┬────────┘ │  │ │
                   │ │  │            │                │        │                 │             │ │
   elektrum-vpc ───┼▶│               │                                           │          │  │ │
                   │ └──┼────────────┼────────────────┼────────┼─────────────────┼─────────────┘ │
                   │                 └─────────────────────┬─────────────────────┘          │    │
                   │    │                             │    │   │                                 │
                   │                                       │                                │    │
                   │    │az: {aws-region}a            │    │   │          az: {aws-region}b      │
                   │     ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─     ▼    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘    │
                   │                                ┌─────────────┐                              │
                   │                                │ elektrum_db │                              │
                   │                                │    [RDS]    │                              │
                   │                                └─────────────┘                              │
                   |               ┌──────────────────────┐ ┌──────────────────────┐             |
                   |               │static.elektrum.photos│ │media.elektrum.photos │             │
                   |               │         [S3]         │ │         [S3]         │             │
                   |               └──────────────────────┘ └──────────────────────┘             │
                   │ aws-region: us-east-1                                                       |
                   └─────────────────────────────────────────────────────────────────────────────┘
```

## NAT Instance

### Routing

**Main Route Table**

* Associated with the private subnets
* Default entry enables instances in the subnet to commmicate with each other.
* Second entry sends all other subnet traffic to the NAT Instance.

<table>
  <thead>
    <tr>
      <th>Target</th>
      <th>CIDR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>NAT Instance ID</td>
      <td><tt>0.0.0.0/0</tt></td>
    </tr>
    <tr>
      <td rowspan="2">Local Traffic</td>
      <td><tt>10.0.1.0/24</tt></td>
    </tr>
    <tr>
      <td><tt>10.0.3.0/24</tt></td>
    </tr>
  </tbody>
</table>

**Custom Route Table**

* Associated with the public subnets
* Default entry enables instances in the subnet to commmicate with each other.
* Second entry routes all other subnet traffic to the internet via the internet gateway.

<table>
  <thead>
    <tr>
      <th>Target</th>
      <th>CIDR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Internet Gateway ID</td>
      <td><tt>0.0.0.0/0</tt></td>
    </tr>
    <tr>
      <td rowspan="2">Local Traffic</td>
      <td><tt>10.0.2.0/24</tt></td>
    </tr>
    <tr>
      <td><tt>10.0.4.0/24</tt></td>
    </tr>
  </tbody>
</table>

### Security Groups

* Allows the NAT instance to receive Internet-bound traffic from instances in the private subnet.

<table>
  <tr>
    <th align="left">Source</th>
    <th align="left">Protocol</th>
    <th align="left">Ports</th>
    <th align="left">Comments</th>
  </tr>
  <tr>
    <th colspan="4" align="left"><i>Inbound</i></th>
  </tr>
  <tr>
    <td>10.0.1.0/24</td>
    <td rowspan="2">HTTP/S</td>
    <td rowspan="2">80 & 443</td>
    <td rowspan="2">Allow inbound HTTP/S traffic for private subnet</td>
  </tr>
  <tr>
    <td>10.0.3.0/24</td>
  </tr>
  <tr>
    <td>Home IP Range</td>
    <td>SSH</td>
    <td>22</td>
    <td>Allow inbound SSH access to the NAT instance.</td>
  </tr>
  <tr><td colspan="4">&nbsp;</td></tr>
  <tr>
    <th colspan="4" align="left"><i>Outbound</i></th>
  </tr>
  <tr>
    <td>0.0.0.0/0</td>
    <td>HTTP/S</td>
    <td>80 & 443</td>
    <td>Allow outbound HTTP/S access to the Internet</td>
  </tr>
</table>

### EC2 Instance

* Use an AMI with `amzn-ami-vpc-nat` in the name.
* Add the instance to the public subnet.
* Assign an Elastic IP address to the instance.
* Associate with the above-described Security Group.
* Disable the `SrcDestCheck` setting.
* Update the _Main Route Table_ to route traffic to this instance.

## Network Layouts

### Production Network

```
Netwrk addr 10.0.0.0/16    00001010.00000000.00000000.00000000
Subnet mask 10.0.0.0/19    11111111.11111111.11100000.00000000
Subnet 1    10.0.0.0/19    00001010.00000000.00000000.00000000
Subnet 2    10.0.32.0/19   00001010.00000000.00100000.00000000
Subnet 3    10.0.64.0/19   00001010.00000000.01000000.00000000
Subnet 4    10.0.96.0/19   00001010.00000000.01100000.00000000
Subnet 5    10.0.128.0/19  00001010.00000000.10000000.00000000 *
Subnet 6    10.0.160.0/19  00001010.00000000.10100000.00000000 *
Subnet 7    10.0.192.0/19  00001010.00000000.11000000.00000000 *
Subnet 8    10.0.224.0/19  00001010.00000000.11100000.00000000 *
```

### Staging Network

```
Netwrk addr 10.64.0.0/16    00001010.01000000.00000000.00000000
Subnet mask 10.64.0.0/19    11111111.11111111.11100000.00000000
Subnet 1    10.64.0.0/19    00001010.01000000.00000000.00000000
Subnet 2    10.64.32.0/19   00001010.01000000.00100000.00000000
Subnet 3    10.64.64.0/19   00001010.01000000.01000000.00000000
Subnet 4    10.64.96.0/19   00001010.01000000.01100000.00000000
Subnet 5    10.64.128.0/19  00001010.01000000.10000000.00000000 *
Subnet 6    10.64.160.0/19  00001010.01000000.10100000.00000000 *
Subnet 7    10.64.192.0/19  00001010.01000000.11000000.00000000 *
Subnet 8    10.64.224.0/19  00001010.01000000.11100000.00000000 *
```

### Development Network

```
Netwrk addr 10.128.0.0/16    00001010.10000000.00000000.00000000
Subnet mask 10.128.0.0/19    11111111.11111111.11100000.00000000
Subnet 1    10.128.0.0/19    00001010.10100000.00000000.00000000
Subnet 2    10.128.32.0/19   00001010.10100000.00100000.00000000
Subnet 3    10.128.64.0/19   00001010.10100000.01000000.00000000
Subnet 4    10.128.96.0/19   00001010.10100000.01100000.00000000
Subnet 5    10.128.128.0/19  00001010.10100000.10000000.00000000 *
Subnet 6    10.128.160.0/19  00001010.10100000.10100000.00000000 *
Subnet 7    10.128.192.0/19  00001010.10100000.11000000.00000000 *
Subnet 8    10.128.224.0/19  00001010.10100000.11100000.00000000 *
```

### Notes

[Calculating a subnet](https://networkengineering.stackexchange.com/questions/7106/how-do-you-calculate-the-prefix-network-subnet-and-host-numbers/53994#53994)

"`*`" indicates these are reserved to scale into a secondary region.

8 Subnets = 2^3
/16 + 3 bits for subnets = /19

19 network bits
13 host bits (8192 addresses per subnet)
