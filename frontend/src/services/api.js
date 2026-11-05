import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

/* HEALTH */
export const getHealth = async () => {
  const response = await API.get("/api/health");
  return response.data;
};

/* OCCUPATIONS */
export const getOccupations = async ({ query = "", limit = 1000 } = {}) => {
  const response = await API.get("/api/intelligence/occupations", {
    params: {
      ...(query.trim() ? { q: query.trim() } : {}),
      limit,
    },
  });

  return response.data;
};

/* OCCUPATION INTELLIGENCE */
export const getOccupationIntelligence = async (occupation) => {
  if (!occupation) {
    throw new Error("Occupation is required.");
  }

  const response = await API.get("/api/intelligence/occupation", {
    params: {
      occupation,
    },
  });

  return response.data;
};

/* FUTURE WORKFORCE SCENARIO */
export const simulateFutureWorkforce = async ({
  occupation,
  baselineAi = 0,
  futureAi = 0.4,
}) => {
  if (!occupation) {
    throw new Error("Occupation is required.");
  }

  const response = await API.get("/api/intelligence/scenario", {
    params: {
      occupation,
      baseline_ai: baselineAi,
      future_ai: futureAi,
    },
  });

  return response.data;
};

/* WORKFORCE REDESIGN */
export const redesignWorkforce = async ({
  occupation,
  aiLevel,
}) => {
  if (!occupation) {
    throw new Error("Occupation is required.");
  }

  const response = await API.get("/api/intelligence/redesign", {
    params: {
      occupation,
      requested_ai: aiLevel,
    },
  });

  return response.data;
};

/* CAPABILITY PRESERVATION */
export const getCapabilityPreservation = async ({
  occupation,
  capability,
}) => {
  if (!occupation) {
    throw new Error("Occupation is required.");
  }

  if (!capability) {
    throw new Error("Capability is required.");
  }

  const response = await API.get("/api/intelligence/preservation", {
    params: {
      occupation,
      capability,
    },
  });

  return response.data;
};

/* COMPLETE FORGE ANALYSIS */
export const getCompleteAnalysis = async ({
  occupation,
  baselineAi = 0,
  futureAi = 0.4,
}) => {
  if (!occupation) {
    throw new Error("Occupation is required.");
  }

  const response = await API.get("/api/intelligence/complete", {
    params: {
      occupation,
      baseline_ai: baselineAi,
      future_ai: futureAi,
    },
  });

  return response.data;
};

/* =========================================================
   LATTICE — REAL GROQ PRACTICE GENERATION
   ========================================================= */

export const generateLatticePractice = async ({
  occupation,
  capability,
}) => {
  if (!occupation) {
    throw new Error("Occupation is required.");
  }

  if (!capability) {
    throw new Error("Capability is required.");
  }

  const response = await API.get("/api/lattice/generate", {
    params: {
      occupation,
      capability,
    },
  });

  return response.data;
};

export default API;