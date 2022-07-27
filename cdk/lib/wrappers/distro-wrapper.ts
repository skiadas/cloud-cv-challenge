// Module that describes how to wrap additions to
// a distribution construction.
// The reason for this convoluted setup is that the
// Distribution class doesn't allow any edits once the
// constructor is called. However many desired additions
// require two conflicting parts:
// - Additions to the props before the constructor is called
// - steps based on the created distribution, after the constructor is called
// The solution is our own Distro class uses the provided
// Distribution class, but which provides for extensions via
// this DistroWrapper interface.

import { DistributionProps, IDistribution } from "aws-cdk-lib/aws-cloudfront";

export interface DistroWrapper {
  alterProps: (props: DistributionProps) => DistributionProps;
  finalizeDistro: (distro: IDistribution) => void;
}
