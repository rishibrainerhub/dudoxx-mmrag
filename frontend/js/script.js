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
      document.getElementById("apiKeyInputaudio").value = apiKey;
      localStorage.setItem("apiKey", apiKey);
      swal("Success", "API Key Generated Successfully!", "success");
    })
    .catch((error) => console.error("Error generating API key:", error));
}

function copyApiKey() {
  const apiKeyInput = document.getElementById("apiKeyInput");
  apiKeyInput.select();
  apiKeyInput.setSelectionRange(0, 99999); // For mobile devices
  document.execCommand("copy");
  swal("Success", "API Key Copied Successfully!", "success");
}

function handleErrors(response) {
  if (!response.ok) {
    if (response.status === 429) {
      throw new Error("Too many requests. Please try again later.");
    } else {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  }
  return response;
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
    .then(handleErrors)
    .then((response) => response.json())
    .then((data) => {
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
      if (error.message.includes("Too many requests")) {
        swal(
          "Error",
          "You've made too many requests in a short time. Please wait a moment and try again.",
          "error"
        );
      } else {
        swal(
          "Error",
          `Failed to fetch drug information. ${error.message}`,
          "error"
        );
      }
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
    .then(handleErrors)
    .then((response) => response.json())
    .then((data) => {
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
      if (error.message.includes("Too many requests")) {
        swal(
          "Error",
          "You've made too many requests in a short time. Please wait a moment and try again.",
          "error"
        );
      } else {
        swal(
          "Error",
          `Failed to fetch disease information. ${error.message}`,
          "error"
        );
      }
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
    .then(handleErrors)
    .then((response) => response.json())
    .then((data) => {
      console.log("Speech generation started:", data);
      statusDiv.innerHTML = `Status: ${data.status}. </p>
      <p><strong>Progress :</strong> ${data.progress}% </p>`;
      
      checkSpeechStatus(data.task_id);
    })
    .catch((error) => {
      swal("Error", `Failed to generate speech. ${error.message}`, "error");
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
    .then(handleErrors)
    .then((response) => response.json())
    .then((data) => {
      console.log("Speech status:", data);
      statusDiv.innerHTML = `<p> Progress: ${data.progress}%</p>
      <p><strong>Status :</strong> ${data.status} </p>
      `;

      if (data.status === "completed") {
        swal("Success", "Speech generation completed successfully!", "success");
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
    .then(handleErrors)
    .then((response) => response.blob())
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `speech_${taskId}.mp3`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      downloadDiv.innerHTML = `<p>Download complete: <a href="${url}" download="speech_${taskId}.mp3">Click here to download</a></p>`;
      swal("Success", "Audio file downloaded successfully!", "success");
    })
    .catch((error) => {
      swal("Error", `Failed to download audio file. ${error.message}`, "error");
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
    swal("Error", "Please select an image file.", "error");
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
    .then(handleErrors)
    .then((response) => response.json())
    .then((data) => {
      imageDescriptionDiv.innerHTML = `<p><strong>Description:</strong> ${data.description}</p>`;
    })
    .catch((error) => {
      if (error.message.includes("Too many requests")) {
        swal(
          "Error",
          "You've made too many requests in a short time. Please wait a moment and try again.",
          "error"
        );
      } else {
        swal("Error", `Failed to describe image. ${error.message}`, "error");
      }
    })
    .finally(() => {
      describeImageButton.innerHTML = "Describe Image";
      describeImageButton.disabled = false;
    });
}

function uploadAudio() {
  const audioInput = document.getElementById("audioInput").files[0];
  const targetLanguage = document.getElementById("targetLanguage").value;
  const uploadAudioButton = document.getElementById("uploadAudioButton");

  if (!audioInput) {
    swal("Error", "Please select an audio file.", "error");
    return;
  }


  // Set button to loading state
  uploadAudioButton.innerHTML = "Uploading...";
  uploadAudioButton.disabled = true;

  const formData = new FormData();
  formData.append("audio", audioInput);

  console.log(targetLanguage)

  fetch(`${url}api/v1/transcribe_audio?target_language=${targetLanguage}`, {
    method: "POST",
    headers: {
      "X-API-Key": localStorage.getItem("apiKey"),
    },
    body: formData,
  })
    .then(handleErrors)
    .then((response) => response.json())
    .then((data) => {
      console.log("Audio upload task started:", data);
      document.getElementById(
        "taskStatus"
      ).innerHTML = `<p><strong>Status :</strong> ${data.status} </p>`;
      checkTaskStatus(data.task_id);
    })
    .catch((error) => {
      swal("Error", `Failed to upload audio. ${error.message}`, "error");
    })
    .finally(() => {
      uploadAudioButton.innerHTML = "Translate Audio";
      uploadAudioButton.disabled = false;
    });
}

function checkTaskStatus(taskId) {
  const taskStatusDiv = document.getElementById("taskStatus");
  const translationResultDiv = document.getElementById("translationResult");
  taskStatusDiv.style.display = "block";
  translationResultDiv.style.display = "block";

  fetch(`${url}api/v1/task_status/${taskId}`, {
    method: "GET",
    headers: {
      "X-API-Key": localStorage.getItem("apiKey"),
    },
  })
    .then(handleErrors)
    .then((response) => response.json())
    .then((data) => {
      // Check if the task is completed and display the results
      if (data.transcription != undefined) {
        swal("Success", "Audio translation completed successfully!", "success");
        taskStatusDiv.innerHTML = `
      <p><strong>Status :</strong> Completed. </p>
      `;

        translationResultDiv.innerHTML = `
      <p><strong>Transcription:</strong> ${data.transcription}</p>
      <p><strong>Translation:</strong> ${data.translation}</p>
    `;
      } else {
        // Continue polling until the task is completed
        setTimeout(() => checkTaskStatus(taskId), 3000);
      }
    })
    .catch((error) => {
      if (error.message.includes("Too many requests")) {
        swal(
          "Error",
          "You've made too many requests in a short time. Please wait a moment and try again.",
          "error"
        );
      } else {
        swal("Error", `Failed to check task status. ${error.message}`, "error");
      }
    });
}

// Load the stored API key on page load
document.addEventListener("DOMContentLoaded", () => {
  const apiKeyInputdrug = document.getElementById("apiKeyInputdrug");
  const storedApiKey = localStorage.getItem("apiKey");
  const apiKeyInputdisease = document.getElementById("apiKeyInputdisease");
  const apiKeyInputvoice = document.getElementById("apiKeyInputvoice");
  const apiKeyInputaudio = document.getElementById("apiKeyInputaudio");

  if (storedApiKey) {
    document.getElementById("apiKeyInput").value = storedApiKey;
    apiKeyInputdrug.value = storedApiKey;
    apiKeyInputdisease.value = storedApiKey;
    apiKeyInputvoice.value = storedApiKey;
    apiKeyInputaudio.value = storedApiKey;
  }
});
