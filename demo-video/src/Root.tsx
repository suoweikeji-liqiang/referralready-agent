import "./index.css";
import { Composition } from "remotion";
import { ReferralReadyDemo } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ReferralReadyDemo"
        component={ReferralReadyDemo}
        durationInFrames={2160}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{}}
      />
    </>
  );
};
