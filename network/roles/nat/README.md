# NAT Instance

## Routing

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

## Security Groups

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

## EC2 Instance

* Use an AMI with `amzn-ami-vpc-nat` in the name.
* Add the instance to the public subnet.
* Assign an Elastic IP address to the instance.
* Associate with the above-described Security Group.
* Disable the `SrcDestCheck` setting.
* Update the _Main Route Table_ to route traffic to this instance.
