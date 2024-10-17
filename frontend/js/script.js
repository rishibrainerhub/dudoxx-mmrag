/* Updated JavaScript (script.js) */
let url = "http://localhost:8000/";

function generateApiKey() {
  const requestOptions = {
    method: "POST",
    redirect: "follow",
  };

  fetch(`${url}api/v1/create_api_key`, requestOptions)
    .then((response) => response.json())
    .then((response) => {
      const apiKey = response.key;
      document.getElementById("apiKeyInput").value = apiKey;
      document.getElementById("apiKeyInputdrug").value = apiKey;
      document.getElementById("apiKeyInputdisease").value = apiKey;
      document.getElementById("apiKeyInputvoice").value = apiKey;
      localStorage.setItem("apiKey", apiKey);
    })
    .catch((error) => console.error("Error generating API key:", error));
}

function copyApiKey() {
  const apiKeyInput = document.getElementById("apiKeyInput");
  apiKeyInput.select();
  apiKeyInput.setSelectionRange(0, 99999); // For mobile devices
  document.execCommand("copy");
  alert("API Key copied to clipboard!");
}

function getDrugInfo() {
  const drugName = document.getElementById("drugName").value.trim();
  const includeInteractions = document.getElementById(
    "includeInteractions"
  ).checked;

  const getDrugInfoButton = document.getElementById("getDrugInfoButton");
  getDrugInfoButton.innerHTML = "Loading...";
  getDrugInfoButton.disabled = true;

  fetch(
    `${url}api/v1/drug_info/${drugName}?include_interactions=${includeInteractions}`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
        "X-API-Key": localStorage.getItem("apiKey"),
      },
    }
  )
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return response.json();
      } else {
        throw new Error("Unexpected response format: not JSON");
      }
    })
    .then((data) => {
      console.log("Drug information:", data);
      const drugInfoDiv = document.getElementById("drugInfo");
      drugInfoDiv.style.display = "block";
      drugInfoDiv.innerHTML = `
        <p><strong>Drug Name:</strong> ${data.name}</p>
        <p><strong>Drug Description:</strong> ${data.description}</p>
        <p><strong>Dosage:</strong> ${data.dosage}</p>
        <p><strong>Side Effects:</strong> ${data.side_effects}</p>
        <p><strong>Interactions:</strong> ${data.interactions}</p>
      `;
    })
    .catch((error) => {
      console.error("Error fetching drug information:", error);
      alert(`Failed to fetch drug information. ${error.message}`);
    })
    .finally(() => {
      getDrugInfoButton.innerHTML = "Get Drug Info";
      getDrugInfoButton.disabled = false;
    });
}

function getDiseaseInfo() {
  const diseaseName = document.getElementById("diseaseName").value.trim();
  const includeTreatments =
    document.getElementById("includeTreatments").checked;

  const getDiseaseInfoButton = document.getElementById("getDiseaseInfoButton");
  getDiseaseInfoButton.innerHTML = "Loading...";
  getDiseaseInfoButton.disabled = true;

  fetch(
    `${url}api/v1/disease_info/${encodeURIComponent(
      diseaseName
    )}?include_treatments=${includeTreatments}`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
        "X-API-Key": localStorage.getItem("apiKey"),
      },
    }
  )
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return response.json();
      } else {
        throw new Error("Unexpected response format: not JSON");
      }
    })
    .then((data) => {
      console.log("Disease information:", data);
      const diseaseInfoDiv = document.getElementById("diseaseInfo");
      diseaseInfoDiv.style.display = "block";
      diseaseInfoDiv.innerHTML = `
        <p><strong>Disease Name:</strong> ${data.name}</p>
        <p><strong>Description:</strong> ${data.description}</p>
        <p><strong>Symptoms:</strong> ${data.symptoms}</p>
        <p><strong>Causes:</strong> ${data.causes}</p>
        <p><strong>Treatments:</strong> ${
          data.treatments ? data.treatments : "Not available"
        }</p>
      `;
    })
    .catch((error) => {
      console.error("Error fetching disease information:", error);
      alert(`Failed to fetch disease information. ${error.message}`);
    })
    .finally(() => {
      getDiseaseInfoButton.innerHTML = "Get Disease Info";
      getDiseaseInfoButton.disabled = false;
    });
}

function generateSpeech() {
  const textInput = document.getElementById("textInput").value.trim();
  const voice = document.getElementById("voiceSelect").value;
  const generateSpeechButton = document.getElementById("generateSpeechButton");
  const statusDiv = document.getElementById("status");

  // Set button to loading state
  generateSpeechButton.innerHTML = "Generating...";
  generateSpeechButton.disabled = true;

  fetch(`${url}api/v1/generate_speech`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "X-API-Key": localStorage.getItem("apiKey"),
    },
    body: JSON.stringify({ text: textInput, voice: voice }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Speech generation started:", data);
      statusDiv.innerHTML = `<p>Task ID: ${data.task_id}. Status: ${data.status}. Progress: ${data.progress}%</p>`;
      checkSpeechStatus(data.task_id);
    })
    .catch((error) => {
      console.error("Error generating speech:", error);
      alert(`Failed to generate speech. ${error.message}`);
    })
    .finally(() => {
      generateSpeechButton.innerHTML = "Generate Speech";
      generateSpeechButton.disabled = false;
    });
}

function checkSpeechStatus(taskId) {
  const statusDiv = document.getElementById("status");
  statusDiv.style.display = "block";

  fetch(`${url}api/v1/speech_status/${taskId}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      "X-API-Key": localStorage.getItem("apiKey"),
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Speech status:", data);
      statusDiv.innerHTML = `<p>Task ID: ${data.task_id}. Status: ${data.status}. Progress: ${data.progress}%</p>`;

      if (data.status === "completed") {
        downloadAudioFile(taskId);
      } else {
        setTimeout(() => checkSpeechStatus(taskId), 3000);
      }
    })
    .catch((error) => {
      console.error("Error checking speech status:", error);
      alert(`Failed to check speech status. ${error.message}`);
    });
}

function downloadAudioFile(taskId) {
  const downloadDiv = document.getElementById("download");
  downloadDiv.style.display = "block";

  fetch(`${url}api/v1/download_speech/${taskId}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      "X-API-Key": localStorage.getItem("apiKey"),
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.blob();
    })
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `speech_${taskId}.mp3`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      downloadDiv.innerHTML = `<p>Download complete: <a href="${url}" download="speech_${taskId}.mp3">Click here to download</a></p>`;
    })
    .catch((error) => {
      console.error("Error downloading audio file:", error);
      alert(`Failed to download audio file. ${error.message}`);
    });
}

function previewImage() {
  const imageInput = document.getElementById("imageInput").files[0];
  const imagePreview = document.getElementById("imagePreview");

  if (imageInput) {
    const reader = new FileReader();
    reader.onload = function (e) {
      imagePreview.src = e.target.result;
      imagePreview.style.display = "block";
    };
    reader.readAsDataURL(imageInput);
  } else {
    imagePreview.style.display = "none";
  }
}

function describeImage() {
  const imageInput = document.getElementById("imageInput").files[0];
  const describeImageButton = document.getElementById("describeImageButton");
  const imageDescriptionDiv = document.getElementById("imageDescription");

  imageDescriptionDiv.style.display = "block";
  if (!imageInput) {
    alert("Please select an image to upload.");
    return;
  }

  // Set button to loading state
  describeImageButton.innerHTML = "Describing...";
  describeImageButton.disabled = true;

  const formData = new FormData();
  formData.append("file", imageInput);

  fetch(
    `${url}api/v1/describe_image?model=gpt-4o&image_size=224&image_size=224`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
        "X-API-Key": localStorage.getItem("apiKey"),
      },
      body: formData,
    }
  )
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Image description:", data);
      imageDescriptionDiv.innerHTML = `<p><strong>Description:</strong> ${data.description}</p>`;
    })
    .catch((error) => {
      console.error("Error describing image:", error);
      alert(`Failed to describe image. ${error.message}`);
    })
    .finally(() => {
      // Reset button value and re-enable it
      describeImageButton.innerHTML = "Describe Image";
      describeImageButton.disabled = false;
    });
}

// Load the stored API key on page load
document.addEventListener("DOMContentLoaded", () => {
  const apiKeyInputdrug = document.getElementById("apiKeyInputdrug");
  const storedApiKey = localStorage.getItem("apiKey");
  const apiKeyInputdisease = document.getElementById("apiKeyInputdisease");
  const apiKeyInputvoice = document.getElementById("apiKeyInputvoice");

  if (storedApiKey) {
    document.getElementById("apiKeyInput").value = storedApiKey;
    apiKeyInputdrug.value = storedApiKey;
    apiKeyInputdisease.value = storedApiKey;
    apiKeyInputvoice.value = storedApiKey;
  }
});
