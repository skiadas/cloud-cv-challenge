// Sets up the cloudfront function for given code file

import { Function, FunctionAssociation, FunctionCode, FunctionEventType } from "aws-cdk-lib/aws-cloudfront";
import { Construct } from "constructs";

export interface CFFunctionProps {
  filePath: string
}

export class CFFunction extends Construct {
  public readonly associations: FunctionAssociation[];
  public readonly function: Function;
  constructor(scope: Construct, id: string, props: CFFunctionProps) {
    super(scope, id);
    const cfFunction = new Function(scope, "redirectForSession", {
      code: FunctionCode.fromFile({
        filePath: props.filePath,
      }),
    });
    this.function = cfFunction;
    this.associations = [
      {
        eventType: FunctionEventType.VIEWER_REQUEST,
        function: cfFunction,
      },
      {
        eventType: FunctionEventType.VIEWER_RESPONSE,
        function: cfFunction,
      },
    ];
  }
}
