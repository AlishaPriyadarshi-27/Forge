import React, { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { Center, useGLTF } from "@react-three/drei";

function EllaModel() {
  const { scene } = useGLTF("/ella/ELLA.glb");

  return (
    <Center>
      <primitive
        object={scene}
        scale={1.7}
        rotation={[0, 0, 0]}
      />
    </Center>
  );
}

export default function EllaAvatar3D() {
  return (
    <div
      style={{
        width: "150px",
        height: "170px",
        position: "relative",
        overflow: "hidden",
        borderRadius: "24px",
      }}
    >
      <Canvas
        camera={{
          position: [0, 1.2, 4],
          fov: 35,
        }}
        dpr={[1, 1.5]}
      >
        <ambientLight intensity={2.2} />

        <directionalLight
          position={[3, 4, 5]}
          intensity={2}
        />

        <directionalLight
          position={[-3, 2, 2]}
          intensity={1}
        />

        <Suspense fallback={null}>
          <EllaModel />
        </Suspense>
      </Canvas>
    </div>
  );
}

useGLTF.preload("/ella/ELLA.glb");