const messageStream = document.getElementById("messageStream");
const quickReplies = document.getElementById("quickReplies");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatWidget = document.getElementById("assistant");
const chatToggle = document.getElementById("chatToggle");
const chatMinimize = document.getElementById("chatMinimize");
const chatReset = document.getElementById("chatReset");
const languageButtons = document.querySelectorAll("[data-lang]");
const dashboardSection = document.getElementById("dashboard");
const doctorLoginOpen = document.getElementById("doctorLoginOpen");
const doctorLoginModal = document.getElementById("doctorLoginModal");
const doctorLoginClose = document.getElementById("doctorLoginClose");
const doctorLoginForm = document.getElementById("doctorLoginForm");
const doctorNameInput = document.getElementById("doctorName");
const doctorCodeInput = document.getElementById("doctorCode");
const doctorIdentity = document.getElementById("doctorIdentity");
const doctorCaseList = document.getElementById("doctorCaseList");
const statTotalConversations = document.getElementById("statTotalConversations");
const statRedFlags = document.getElementById("statRedFlags");
const statBookingDrafts = document.getElementById("statBookingDrafts");

const caseTitle = document.getElementById("caseTitle");
const priorityPill = document.getElementById("priorityPill");
const symptomValue = document.getElementById("symptomValue");
const relationValue = document.getElementById("relationValue");
const ageValue = document.getElementById("ageValue");
const severityValue = document.getElementById("severityValue");
const specialtyValue = document.getElementById("specialtyValue");
const bookingValue = document.getElementById("bookingValue");
const doctorSummary = document.getElementById("doctorSummary");
const queueLiveTitle = document.getElementById("queueLiveTitle");
const queueLiveMeta = document.getElementById("queueLiveMeta");

const DEFAULT_LANGUAGE = "vi";
const LANGUAGE_STORAGE_KEY = "vinmec_ai_demo_language";
const API_BASE_STORAGE_KEY = "vinmec_ai_demo_api_base_url";

function getApiBaseUrl() {
  const params = new URLSearchParams(window.location.search);
  const queryApiBase = params.get("api");
  if (queryApiBase) {
    const cleanedApiBase = queryApiBase.replace(/\/+$/, "");
    localStorage.setItem(API_BASE_STORAGE_KEY, cleanedApiBase);
    return cleanedApiBase;
  }
  const storedApiBase = localStorage.getItem(API_BASE_STORAGE_KEY);
  if (storedApiBase) {
    return storedApiBase.replace(/\/+$/, "");
  }
  if (window.VINMEC_API_BASE_URL) {
    return window.VINMEC_API_BASE_URL.replace(/\/+$/, "");
  }
  return "http://127.0.0.1:8000";
}

const API_BASE_URL = getApiBaseUrl();

const state = {
  language: getInitialLanguage(),
  caseId: generateCaseId(),
  backendSessionId: "",
  backendCaseId: "",
  backendPatientId: "",
  backendAvailable: true,
  doctorAuthenticated: false,
  doctorName: "",
  doctorCode: "",
  doctorCases: [],
  doctorStats: null,
  selectedDoctorCaseId: "",
  step: "welcome",
  symptomText: "",
  relationCode: "",
  relationText: "",
  age: "",
  severityCode: "",
  severityText: "",
  specialtyKey: "",
  specialtyText: "",
  triage: "waiting",
  priority: "waiting",
  redFlags: [],
  redFlagText: "",
  bookingIntent: false,
  preferredHospitalKey: "",
  preferredHospitalText: "",
  preferredTimeKey: "",
  preferredTimeText: "",
  bookingStatus: "not_started",
  doctorSummary: "",
  backendDoctorSummary: "",
  history: []
};

const I18N = {
  vi: {
    page: {
      title: "Vinmec AI Intake Demo Song Ngữ"
    },
    common: {
      english: "English",
      vietnamese: "Tiếng Việt"
    },
    utility: {
      demoLayer: "Lớp demo AI Intake",
      searchDoctor: "Tìm bác sĩ",
      customerService: "Chăm sóc khách hàng"
    },
    nav: {
      about: "Về Vinmec",
      medicalTourism: "Du lịch y tế",
      specialties: "Chuyên khoa",
      csr: "CSR & ESG",
      services: "Dịch vụ & gói khám",
      blog: "Blog sức khỏe",
      customers: "Dành cho khách hàng"
    },
    header: {
      experience: "Trải nghiệm AI Agent"
    },
    hero: {
      kicker: "Hệ thống Y tế Quốc tế Vinmec",
      title: "Chăm sóc bằng sự tận tâm, chuyên môn và trí tuệ",
      body: "Bản demo này giữ cảm giác quen thuộc của homepage Vinmec, sau đó gắn thêm AI intake agent nổi để tiếp nhận triệu chứng, phát hiện red flag và hỗ trợ đặt lịch ngay trên trang.",
      openAgent: "Mở AI Agent",
      handoff: "Xem handoff cho bác sĩ"
    },
    cta: {
      consult: {
        title: "Tư vấn",
        body: "Nhận tư vấn từ đội ngũ chuyên môn của Vinmec."
      },
      booking: {
        title: "Đặt lịch",
        body: "Đặt lịch hẹn với Vinmec."
      },
      findDoctor: {
        title: "Tìm bác sĩ",
        body: "Duyệt danh sách bác sĩ và chuyên gia."
      }
    },
    why: {
      kicker: "Lớp trang chủ",
      title: "Vì sao chọn Vinmec?",
      card1: {
        title: "Đội ngũ chuyên môn hàng đầu",
        body: "Các chuyên gia, bác sĩ, dược sĩ và điều dưỡng được giới thiệu như một đội ngũ chăm sóc cao cấp lấy người bệnh làm trung tâm."
      },
      card2: {
        title: "Tiêu chuẩn quốc tế",
        body: "Vận hành, quản trị và trải nghiệm bệnh nhân được định vị theo hệ thống hiện đại và chuẩn chăm sóc mang tính toàn cầu."
      },
      card3: {
        title: "Công nghệ tiên tiến",
        body: "Cơ sở vật chất cao cấp và công nghệ lâm sàng hiện đại được nhấn mạnh như một phần của trải nghiệm y tế 5 sao."
      },
      card4: {
        title: "Nghiên cứu & đổi mới",
        body: "Y học hàn lâm, hợp tác quốc tế và đổi mới y khoa được xem là động lực cho điều trị đột phá và chăm sóc tốt hơn."
      }
    },
    awards: {
      kicker: "Công nhận",
      title: "Thành tựu và giải thưởng",
      body: "Các chứng nhận và ghi nhận quốc tế giúp phần nền của demo tiến gần hơn với homepage Vinmec thực tế."
    },
    network: {
      kicker: "Hệ thống y tế",
      title: "Mạng lưới bệnh viện và trung tâm",
      body: "Trang Vinmec thực nhấn mạnh hệ thống phủ rộng toàn quốc, các bệnh viện đạt chuẩn JCI và tiêu chuẩn an toàn người bệnh cao. Phiên bản này tái hiện đúng lớp kể chuyện đó để AI widget trông như được gắn vào một môi trường Vinmec đáng tin cậy.",
      link: "Khám phá đối tác",
      hospital1: "Bệnh viện mũi nhọn trong đô thị với thế mạnh quốc tế và nhiều chuyên khoa sâu.",
      hospital2: "Điểm hiện diện tại TP.HCM với cơ sở vật chất cao cấp và workflow lâm sàng hiện đại.",
      hospital3: "Mở rộng khả năng tiếp cận dịch vụ tại khu vực du lịch và thành phố biển.",
      hospital4: "Đại diện cho miền Trung trong cùng một ngôn ngữ thiết kế bệnh viện quốc tế.",
      hospital5: "Một mắt xích khác trong câu chuyện mạng lưới chăm sóc trên homepage English.",
      hospital6: "Hình ảnh cơ sở mới giúp phần nền bám sát hơn với website Vinmec đang vận hành."
    },
    partners: {
      kicker: "Kết nối toàn cầu",
      title: "Đối tác"
    },
    sync: {
      kicker: "Lớp phủ hackathon",
      title: "Lớp AI Intake đặt trên homepage",
      body: "Phần nền giờ bám theo cấu trúc homepage Vinmec, còn khu vực phía dưới tiếp tục hiển thị dữ liệu handoff live cho phần demo của bạn.",
      currentCase: "Ca hiện tại",
      queuePreview: "Xem nhanh hàng đợi bác sĩ",
      demoQueue: "Hàng đợi demo",
      sampleMedium: "Mẹ người dùng đau dạ dày 2 tuần, booking draft tại Times City.",
      sampleHigh: "Người dùng đau ngực, khó thở. Emergency handoff cho CSKH."
    },
    dashboard: {
      symptom: "Triệu chứng chính",
      relation: "Người bệnh",
      age: "Tuổi / năm sinh",
      severity: "Mức độ",
      specialty: "Chuyên khoa gợi ý",
      booking: "Đặt lịch",
      summaryLabel: "Doctor summary",
      caseNotStarted: "Ca chưa khởi tạo",
      notProvided: "Chưa có",
      notStarted: "Chưa bắt đầu",
      noRegularBooking: "Không tạo booking thường",
      waiting: "Chờ",
      summaryEmpty: "Bắt đầu cuộc trò chuyện để xem case summary được dựng tự động từ intake flow.",
      draftPrefix: "Draft",
      intakeInProgress: "Đang intake",
      patientUnknown: "Người bệnh chưa rõ",
      severityUnknown: "Chưa rõ mức độ",
      bookingReady: "Đã có booking draft.",
      bookingMissing: "Chưa có booking.",
      statusEmergency: "Emergency handoff.",
      statusContinue: "Tiếp tục intake / booking.",
      summaryTemplate: "Người bệnh: {relation}. Tuổi: {age}. Triệu chứng chính: {symptom}. Mức độ: {severity}. Red flag: {redFlags}. Chuyên khoa gợi ý: {specialty}. Trạng thái: {status} {bookingSentence}",
      bookingSentenceDraft: "Booking draft tại {hospital} - {time}.",
      bookingSentenceNone: "Chưa tạo booking draft.",
      queueTitleActive: "Case #{caseId} · {specialty}",
      queueMetaEmergency: "Emergency handoff vì: {redFlags}.",
      queueMetaActive: "{relation} · {severity} · {bookingStatus}"
    },
    chatUi: {
      eyebrow: "Vinmec AI Agent",
      title: "Tôi có thể giúp gì cho bạn hôm nay?",
      formLabel: "Nhập câu hỏi cho AI agent",
      placeholder: "Ví dụ: Tôi đau dạ dày, đầy hơi 2 tuần nay",
      send: "Gửi",
      disclaimer: "Demo intake assistant: không thay thế chẩn đoán y khoa. Nếu phát hiện red flag, agent sẽ ưu tiên cảnh báo và đề nghị liên hệ khẩn cấp.",
      toggleAria: "Mở hoặc thu gọn AI agent",
      sectionAria: "Vinmec AI agent",
      minimizeAria: "Thu gọn chat",
      typingAria: "AI đang nhập"
    },
    chat: {
      welcomeText: "Chào bạn, tôi là Vinmec AI Agent. Tôi có thể giúp gì cho bạn hôm nay? Bạn có thể mô tả triệu chứng, hỏi chuyên khoa phù hợp hoặc bắt đầu một booking draft.",
      welcomeReplySymptoms: "Tôi muốn khai báo triệu chứng",
      welcomeReplySpecialty: "Tìm chuyên khoa phù hợp",
      welcomeReplyBooking: "Hỗ trợ đặt lịch khám ảo",
      askInitialSymptom: "Bạn hãy mô tả ngắn triệu chứng hoặc vấn đề sức khỏe đang muốn Vinmec hỗ trợ nhé.",
      askRelation: "Mình cần hỏi thêm vài thông tin để định hướng đúng hơn. Người đang có triệu chứng là bạn hay người thân?",
      askAge: "Bạn cho mình xin tuổi hoặc năm sinh của người bệnh để intake case rõ hơn nhé.",
      askAgeRetry: "Mình chưa nhận ra tuổi hoặc năm sinh. Bạn nhập theo dạng như 58 tuổi hoặc sinh năm 1970 nhé.",
      askSeverity: "Mức độ khó chịu hiện tại ở mức nào?",
      askSeverityRetry: "Bạn chọn giúp mình mức độ: Nhẹ, Vừa, Nặng hoặc Rất nặng / không chịu được nhé.",
      safeNoEmergency: "Hiện chưa thấy dấu hiệu khẩn cấp từ thông tin bạn đã cung cấp.",
      safeSpecialty: "Với triệu chứng hiện tại, bạn nên cân nhắc khám {specialty}. Nếu xuất hiện thêm các dấu hiệu như {warningSigns}, bạn cần đi khám sớm hơn.",
      safeBookingPrompt: "Bạn có muốn mình hỗ trợ tạo lịch khám ảo nháp ngay trong chat không?",
      emergency: "Triệu chứng bạn mô tả có thể là dấu hiệu cần được xử lý khẩn cấp. Mình không tiếp tục tư vấn từ xa trong trường hợp này. Bạn nên gọi hotline Vinmec hoặc đến cơ sở y tế gần nhất ngay. Dashboard sẽ ghi nhận case ưu tiên cao để CSKH/bác sĩ tiếp nhận.",
      bookingCreated: "Mình đã tạo booking draft cho bạn: {specialty} tại {hospital}, thời gian mong muốn {time}. Toàn bộ case summary và lịch sử chat đã sẵn sàng để đội Vinmec tiếp nhận.",
      askHospital: "Bạn muốn khám tại cơ sở nào?",
      askTime: "Bạn muốn đặt lịch vào khoảng thời gian nào?",
      bookingConfirm: "Mình xác nhận lại: {relation}, {age}, triệu chứng \"{symptom}\", chuyên khoa {specialty}, cơ sở {hospital}, thời gian {time}. Bạn muốn tạo booking draft với thông tin này không?",
      askMoreContinue: "Bạn cứ nhập thêm triệu chứng hoặc điều bạn đang băn khoăn, mình sẽ tiếp tục hỗ trợ trong cùng case này.",
      caseSavedMonitor: "Mình đã lưu case để bạn theo dõi thêm. Nếu bạn muốn, mình vẫn có thể tạo booking draft bất cứ lúc nào.",
      reaskHospital: "Không sao, mình sẽ hỏi lại từ phần cơ sở khám nhé. Bạn muốn khám ở đâu?",
      bookingCancelled: "Mình đã hủy booking draft hiện tại. Nếu bạn muốn, mình vẫn có thể hỗ trợ lại bất cứ lúc nào.",
      emergencyFollowup: "Mình đã đánh dấu case ưu tiên cao. Nếu bạn vẫn còn triệu chứng, vui lòng liên hệ ngay cơ sở y tế gần nhất.",
      bookingHold: "Mình đã giữ nguyên booking draft hiện tại. Nếu cần, bạn có thể tiếp tục đặt câu hỏi hoặc tạo một case mới.",
      understood: "Tôi đã hiểu",
      reenterSymptoms: "Tôi muốn nhập lại triệu chứng",
      askMore: "Tôi muốn hỏi thêm",
      newCase: "Tạo ca mới",
      bookVirtual: "Đặt lịch khám ảo",
      monitorMore: "Để tôi theo dõi thêm",
      confirm: "Xác nhận",
      editInfo: "Sửa thông tin",
      cancel: "Hủy"
    }
  },
  en: {
    page: {
      title: "Vinmec Bilingual AI Intake Demo"
    },
    common: {
      english: "English",
      vietnamese: "Tiếng Việt"
    },
    utility: {
      demoLayer: "AI Intake Demo Layer",
      searchDoctor: "Search for a doctor",
      customerService: "Customer Service"
    },
    nav: {
      about: "About Us",
      medicalTourism: "Medical Tourism",
      specialties: "Hospital Specialties",
      csr: "CSR & ESG",
      services: "Service & Packages",
      blog: "Health Blog",
      customers: "For Customers"
    },
    header: {
      experience: "Experience AI Agent"
    },
    hero: {
      kicker: "Vinmec International Healthcare System",
      title: "We care with compassion, professionalism and wisdom",
      body: "This demo keeps the familiar Vinmec homepage feeling, then adds a floating AI intake agent that can collect symptoms, detect red flags and guide booking right on top of the page.",
      openAgent: "Open AI Agent",
      handoff: "View doctor handoff"
    },
    cta: {
      consult: {
        title: "Consult",
        body: "Get consulted by our professionals."
      },
      booking: {
        title: "Booking",
        body: "Make appointments with Vinmec."
      },
      findDoctor: {
        title: "Find a Doctor",
        body: "Browse the professionals directory."
      }
    },
    why: {
      kicker: "Homepage Layer",
      title: "Why Vinmec?",
      card1: {
        title: "Top-tier professionals",
        body: "Specialists, doctors, pharmacists and nurses are presented as a premium care team focused on patient-centered service."
      },
      card2: {
        title: "International standards",
        body: "Operations, management and patient experience are positioned around modern systems and a globally recognizable care standard."
      },
      card3: {
        title: "Advanced technologies",
        body: "High-end facilities and advanced clinical technologies are highlighted as part of a five-star healthcare experience."
      },
      card4: {
        title: "Research & Innovation",
        body: "Academic medicine, global partnerships and medical innovation are framed as drivers for better care and breakthrough treatment."
      }
    },
    awards: {
      kicker: "Recognition",
      title: "Achievements and Awards",
      body: "Public certifications and international recognitions help the demo background feel much closer to the real Vinmec homepage."
    },
    network: {
      kicker: "Healthcare System",
      title: "Our network of clinics and centers",
      body: "The real Vinmec page emphasizes a nationwide system, JCI-recognized hospitals and high patient-safety standards. This version recreates that same storytelling layer so the AI widget feels embedded into a believable Vinmec environment.",
      link: "Explore partners",
      hospital1: "A flagship urban campus for international care and specialist services.",
      hospital2: "A Ho Chi Minh City presence with premium facilities and a modern clinical workflow.",
      hospital3: "Expands access to care in a tourism-focused coastal city.",
      hospital4: "Represents Central Vietnam in the same international-hospital visual language.",
      hospital5: "Another node in the care network story shown on the English homepage.",
      hospital6: "Newer campus imagery helps the background stay close to the live Vinmec website."
    },
    partners: {
      kicker: "Global Connections",
      title: "Our Partners"
    },
    sync: {
      kicker: "Hackathon Overlay",
      title: "AI Intake Layer on top of the homepage",
      body: "The background now follows Vinmec's homepage structure, while this lower section continues to show the live handoff data for your demo.",
      currentCase: "Current case",
      queuePreview: "Doctor queue preview",
      demoQueue: "Demo queue",
      sampleMedium: "User's mother with stomach pain for 2 weeks, booking draft at Times City.",
      sampleHigh: "User with chest pain and shortness of breath. Emergency handoff for CSKH."
    },
    dashboard: {
      symptom: "Main symptom",
      relation: "Patient",
      age: "Age / birth year",
      severity: "Severity",
      specialty: "Suggested specialty",
      booking: "Booking",
      summaryLabel: "Doctor summary",
      caseNotStarted: "Case not started",
      notProvided: "Not provided",
      notStarted: "Not started",
      noRegularBooking: "Regular booking disabled",
      waiting: "Waiting",
      summaryEmpty: "Start the conversation to see the auto-generated case summary from the intake flow.",
      draftPrefix: "Draft",
      intakeInProgress: "Intake in progress",
      patientUnknown: "Patient not identified",
      severityUnknown: "Severity not set",
      bookingReady: "Booking draft created.",
      bookingMissing: "No booking yet.",
      statusEmergency: "Emergency handoff.",
      statusContinue: "Continue intake / booking.",
      summaryTemplate: "Patient: {relation}. Age: {age}. Main symptom: {symptom}. Severity: {severity}. Red flags: {redFlags}. Suggested specialty: {specialty}. Status: {status} {bookingSentence}",
      bookingSentenceDraft: "Booking draft at {hospital} - {time}.",
      bookingSentenceNone: "No booking draft created.",
      queueTitleActive: "Case #{caseId} · {specialty}",
      queueMetaEmergency: "Emergency handoff because of: {redFlags}.",
      queueMetaActive: "{relation} · {severity} · {bookingStatus}"
    },
    chatUi: {
      eyebrow: "Vinmec AI Agent",
      title: "How can I help you today?",
      formLabel: "Type a question for the AI agent",
      placeholder: "Example: I have stomach pain and bloating for 2 weeks",
      send: "Send",
      disclaimer: "Intake assistant demo: this does not replace medical diagnosis. If red flags are detected, the agent will prioritize an emergency recommendation.",
      toggleAria: "Open or collapse the AI agent",
      sectionAria: "Vinmec AI agent",
      minimizeAria: "Collapse chat",
      typingAria: "AI is typing"
    },
    chat: {
      welcomeText: "Hello, I'm the Vinmec AI Agent. How can I help you today? You can describe symptoms, ask for the right specialty, or start a booking draft.",
      welcomeReplySymptoms: "I want to describe symptoms",
      welcomeReplySpecialty: "Find the right specialty",
      welcomeReplyBooking: "Help me book a virtual visit",
      askInitialSymptom: "Please describe the symptom or health concern you want Vinmec to support.",
      askRelation: "I need a few more details to guide this correctly. Are these symptoms yours or a family member's?",
      askAge: "Please share the patient's age or birth year so I can build the intake case more clearly.",
      askAgeRetry: "I couldn't detect the age or birth year yet. Please enter it like 58 years old or born in 1970.",
      askSeverity: "How uncomfortable is it right now?",
      askSeverityRetry: "Please choose the severity: Mild, Moderate, Severe, or Very severe / unbearable.",
      safeNoEmergency: "At the moment, I do not see emergency warning signs from the information you shared.",
      safeSpecialty: "Based on the current symptoms, you should consider seeing {specialty}. If signs such as {warningSigns} appear, you should seek care sooner.",
      safeBookingPrompt: "Would you like me to create a virtual visit booking draft in this chat?",
      emergency: "The symptoms you described may need urgent medical attention. I should not continue remote guidance in this situation. Please call the Vinmec hotline or go to the nearest medical facility right away. The dashboard will mark this case as high priority for the care team.",
      bookingCreated: "I've created a booking draft for you: {specialty} at {hospital}, preferred time {time}. The full case summary and chat history are ready for the Vinmec team.",
      askHospital: "Which facility would you like to visit?",
      askTime: "What time would you prefer for the appointment?",
      bookingConfirm: "Let me confirm: {relation}, {age}, symptom \"{symptom}\", specialty {specialty}, facility {hospital}, time {time}. Would you like me to create the booking draft with this information?",
      askMoreContinue: "Feel free to add more symptoms or questions and I'll continue supporting this same case.",
      caseSavedMonitor: "I've saved the case so you can monitor it further. If you want, I can still create a booking draft at any time.",
      reaskHospital: "No problem, I'll ask again from the facility step. Which location would you prefer?",
      bookingCancelled: "I've canceled the current booking draft. If you want, I can help create it again anytime.",
      emergencyFollowup: "I've marked this as a high-priority case. If symptoms are still present, please contact the nearest medical facility immediately.",
      bookingHold: "I've kept the current booking draft unchanged. If needed, you can continue asking questions or create a new case.",
      understood: "Understood",
      reenterSymptoms: "I want to re-enter symptoms",
      askMore: "I want to ask more",
      newCase: "Create a new case",
      bookVirtual: "Book a virtual visit",
      monitorMore: "Let me monitor it first",
      confirm: "Confirm",
      editInfo: "Edit info",
      cancel: "Cancel"
    }
  }
};

const RELATIONS = {
  self: {
    label: { vi: "Người dùng", en: "User" },
    reply: { vi: "Tôi", en: "Myself" }
  },
  mother: {
    label: { vi: "Mẹ của người dùng", en: "User's mother" },
    reply: { vi: "Mẹ tôi", en: "My mother" }
  },
  father: {
    label: { vi: "Bố của người dùng", en: "User's father" },
    reply: { vi: "Bố tôi", en: "My father" }
  },
  child: {
    label: { vi: "Con của người dùng", en: "User's child" },
    reply: { vi: "Con tôi", en: "My child" }
  },
  other: {
    label: { vi: "Người thân khác", en: "Another family member" },
    reply: { vi: "Người thân khác", en: "Another family member" }
  }
};

const SEVERITIES = {
  mild: {
    label: { vi: "Nhẹ", en: "Mild" }
  },
  moderate: {
    label: { vi: "Vừa", en: "Moderate" }
  },
  severe: {
    label: { vi: "Nặng", en: "Severe" }
  },
  very_severe: {
    label: { vi: "Rất nặng", en: "Very severe" },
    reply: { vi: "Rất nặng / không chịu được", en: "Very severe / unbearable" }
  }
};

const HOSPITALS = {
  times_city: {
    label: { vi: "Vinmec Times City", en: "Vinmec Times City" },
    keywords: ["times city", "vinmec times city"]
  },
  central_park: {
    label: { vi: "Vinmec Central Park", en: "Vinmec Central Park" },
    keywords: ["central park", "vinmec central park"]
  },
  da_nang: {
    label: { vi: "Vinmec Đà Nẵng", en: "Vinmec Da Nang" },
    keywords: ["da nang", "vinmec da nang", "vinmec đà nẵng"]
  },
  not_sure: {
    label: { vi: "Chưa chắc", en: "Not sure yet" },
    keywords: ["chua chac", "not sure", "not sure yet"]
  }
};

const TIME_WINDOWS = {
  tomorrow_morning: {
    label: { vi: "Sáng mai", en: "Tomorrow morning" },
    keywords: ["sang mai", "tomorrow morning"]
  },
  tomorrow_afternoon: {
    label: { vi: "Chiều mai", en: "Tomorrow afternoon" },
    keywords: ["chieu mai", "tomorrow afternoon"]
  },
  weekend: {
    label: { vi: "Cuối tuần", en: "This weekend" },
    keywords: ["cuoi tuan", "this weekend", "weekend"]
  },
  choose_later: {
    label: { vi: "Chọn sau", en: "Choose later" },
    keywords: ["chon sau", "choose later", "later"]
  }
};

const SPECIALTY_RULES = [
  {
    key: "gastro",
    label: { vi: "Nội Tiêu hóa", en: "Gastroenterology" },
    keywords: [
      "da day",
      "day hoi",
      "kho tieu",
      "dau bung",
      "tieu hoa",
      "o chua",
      "stomach pain",
      "bloating",
      "indigestion",
      "abdominal pain",
      "digestive",
      "acid reflux"
    ],
    guidance: {
      vi: [
        "Ăn nhẹ và chia nhỏ bữa.",
        "Tránh đồ cay, nhiều dầu mỡ và rượu bia.",
        "Uống đủ nước và theo dõi thêm triệu chứng."
      ],
      en: [
        "Eat light meals and split meals into smaller portions.",
        "Avoid spicy, oily foods and alcohol for now.",
        "Stay hydrated and keep monitoring the symptoms."
      ]
    },
    warningSigns: {
      vi: ["Đau bụng dữ dội", "Nôn ra máu", "Đi ngoài phân đen", "Sốt cao kéo dài"],
      en: ["Severe abdominal pain", "Vomiting blood", "Black stools", "Persistent high fever"]
    }
  },
  {
    key: "respiratory",
    label: { vi: "Hô hấp", en: "Respiratory Medicine" },
    keywords: [
      "ho",
      "sot",
      "kho tho",
      "viem hong",
      "dom",
      "cough",
      "fever",
      "shortness of breath",
      "sore throat",
      "phlegm"
    ],
    guidance: {
      vi: [
        "Nghỉ ngơi và uống đủ nước.",
        "Theo dõi sốt, ho kéo dài hoặc mệt tăng dần.",
        "Đeo khẩu trang khi có triệu chứng hô hấp."
      ],
      en: [
        "Rest and drink enough water.",
        "Monitor persistent fever, cough, or worsening fatigue.",
        "Wear a mask if you have respiratory symptoms."
      ]
    },
    warningSigns: {
      vi: ["Khó thở tăng dần", "Tím tái", "Sốt cao không hạ", "Lơ mơ"],
      en: ["Worsening shortness of breath", "Bluish lips or skin", "High fever that won't go down", "Confusion"]
    }
  },
  {
    key: "cardiology",
    label: { vi: "Tim mạch", en: "Cardiology" },
    keywords: [
      "dau nguc",
      "tim",
      "hoi hop",
      "chong mat",
      "chest pain",
      "heart",
      "palpitations",
      "dizziness"
    ],
    guidance: {
      vi: [
        "Tránh gắng sức mạnh trong lúc chờ đánh giá.",
        "Ghi nhận thời điểm xuất hiện cơn đau hoặc hồi hộp.",
        "Nếu đau ngực hoặc khó thở xuất hiện lại, cần đi cấp cứu ngay."
      ],
      en: [
        "Avoid intense physical exertion while waiting for evaluation.",
        "Note when the pain or palpitations happen.",
        "If chest pain or shortness of breath returns, seek emergency care immediately."
      ]
    },
    warningSigns: {
      vi: ["Đau ngực kéo dài", "Khó thở", "Ngất", "Vã mồ hôi lạnh"],
      en: ["Persistent chest pain", "Shortness of breath", "Fainting", "Cold sweating"]
    }
  },
  {
    key: "musculoskeletal",
    label: { vi: "Cơ xương khớp", en: "Musculoskeletal" },
    keywords: [
      "dau lung",
      "dau khop",
      "dau goi",
      "vai gay",
      "xuong",
      "back pain",
      "joint pain",
      "knee pain",
      "neck pain",
      "bone"
    ],
    guidance: {
      vi: [
        "Giảm tải vận động mạnh ở vùng đau.",
        "Theo dõi sưng nóng đỏ hoặc hạn chế vận động.",
        "Chườm ấm hoặc lạnh tùy tình huống nếu không có chống chỉ định."
      ],
      en: [
        "Reduce heavy activity around the painful area.",
        "Watch for swelling, heat, redness, or limited movement.",
        "Use warm or cold compresses if appropriate."
      ]
    },
    warningSigns: {
      vi: ["Yếu liệt", "Đau tăng nhanh", "Biến dạng", "Sốt kèm đau khớp"],
      en: ["Weakness or paralysis", "Rapidly worsening pain", "Deformity", "Fever with joint pain"]
    }
  }
];

const DEFAULT_SPECIALTY = {
  key: "general",
  label: { vi: "Nội tổng quát", en: "General Internal Medicine" },
  guidance: {
    vi: [
      "Theo dõi diễn tiến triệu chứng trong ngày.",
      "Uống đủ nước và nghỉ ngơi phù hợp.",
      "Nếu triệu chứng tăng nhanh hoặc xuất hiện dấu hiệu bất thường, cần đi khám sớm."
    ],
    en: [
      "Monitor how the symptoms change during the day.",
      "Stay hydrated and rest appropriately.",
      "If symptoms worsen quickly or new unusual signs appear, seek medical care soon."
    ]
  },
  warningSigns: {
    vi: ["Đau tăng nhanh", "Khó thở", "Sốt cao", "Lơ mơ"],
    en: ["Rapidly worsening pain", "Shortness of breath", "High fever", "Confusion"]
  }
};

const RED_FLAG_RULES = [
  {
    code: "chest_pain",
    keywords: ["dau nguc", "tuc nguc", "dau nguc lan tay", "dau nguc lan ham", "dau nguc lan lung", "chest pain"],
    label: { vi: "Đau ngực", en: "Chest pain" }
  },
  {
    code: "shortness_of_breath",
    keywords: ["kho tho", "kho tho tang dan", "moi tim", "shortness of breath", "difficulty breathing", "blue lips"],
    label: { vi: "Khó thở", en: "Shortness of breath" }
  },
  {
    code: "vomiting_blood",
    keywords: ["non ra mau", "oi ra mau", "vomiting blood", "vomit blood"],
    label: { vi: "Nôn ra máu", en: "Vomiting blood" }
  },
  {
    code: "black_stools",
    keywords: ["phan den", "di ngoai ra mau", "tieu chay ra mau", "black stool", "black stools", "bloody stool"],
    label: { vi: "Đi ngoài phân đen", en: "Black stools" }
  },
  {
    code: "seizure",
    keywords: ["co giat", "seizure", "seizures"],
    label: { vi: "Co giật", en: "Seizure" }
  },
  {
    code: "fainting",
    keywords: ["ngat", "lo mo", "choang vang", "faint", "fainting", "confused", "confusion"],
    label: { vi: "Ngất/lơ mơ", en: "Fainting or confusion" }
  },
  {
    code: "very_high_fever",
    keywords: ["sot 40", "sot cao khong ha", "ret run", "fever 40", "40 degree fever"],
    label: { vi: "Sốt rất cao", en: "Very high fever" }
  },
  {
    code: "heavy_bleeding",
    keywords: ["chay mau nhieu", "heavy bleeding"],
    label: { vi: "Chảy máu nhiều", en: "Heavy bleeding" }
  },
  {
    code: "swelling_after_drug_food",
    keywords: ["sung moi", "sung mat", "sung luoi", "sung hong", "phat ban kem kho tho", "swollen lips", "swollen face", "swollen tongue", "throat swelling"],
    label: { vi: "Sưng môi/mặt/lưỡi", en: "Swelling of lips, face, or tongue" }
  },
  {
    code: "stroke_signs",
    keywords: ["meo mieng", "noi kho", "yeu nua nguoi", "te nua nguoi", "mat thi luc dot ngot"],
    label: { vi: "Dấu hiệu thần kinh cấp", en: "Acute neurologic signs" }
  },
  {
    code: "severe_headache",
    keywords: ["dau dau du doi", "dau dau dot ngot", "co gay"],
    label: { vi: "Đau đầu dữ dội/đột ngột", en: "Severe sudden headache" }
  },
  {
    code: "severe_abdominal",
    keywords: ["dau bung du doi", "dau bung tang dan", "bung cung", "non lien tuc", "non mau ca phe"],
    label: { vi: "Đau bụng/nôn nghiêm trọng", en: "Severe abdominal symptoms" }
  },
  {
    code: "urinary_retention",
    keywords: ["khong tieu duoc", "bi tieu"],
    label: { vi: "Bí tiểu", en: "Urinary retention" }
  },
  {
    code: "spinal_compression",
    keywords: ["te vung yen ngua", "mat kiem soat tieu tien", "mat kiem soat dai tien"],
    label: { vi: "Dấu hiệu chèn ép thần kinh", en: "Spinal compression signs" }
  },
  {
    code: "pregnancy_emergency",
    keywords: ["mang thai ra mau", "mang thai dau bung", "thai may yeu"],
    label: { vi: "Dấu hiệu nguy hiểm thai kỳ", en: "Pregnancy warning signs" }
  },
  {
    code: "child_emergency",
    keywords: ["tre li bi", "tre kho danh thuc", "tre kho tho", "tre co giat", "tre mat nuoc"],
    label: { vi: "Dấu hiệu nguy hiểm ở trẻ", en: "Child emergency signs" }
  }
];

function getInitialLanguage() {
  try {
    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    return stored === "en" || stored === "vi" ? stored : DEFAULT_LANGUAGE;
  } catch {
    return DEFAULT_LANGUAGE;
  }
}

function generateCaseId() {
  return `VM-${Math.floor(100 + Math.random() * 900)}`;
}

function getByPath(object, path) {
  return path.split(".").reduce((value, part) => (value ? value[part] : undefined), object);
}

function t(path, language = state.language) {
  return getByPath(I18N[language], path) ?? path;
}

function format(path, values = {}, language = state.language) {
  return Object.entries(values).reduce(
    (result, [key, value]) => result.replaceAll(`{${key}}`, value),
    t(path, language)
  );
}

function normalizeForMatch(value) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function matchesAny(text, keywords) {
  return keywords.some((keyword) => text.includes(keyword));
}

function knownOrEmpty(value) {
  return value && value !== "unknown" ? value : "";
}

function relationCodeFromBackend(value) {
  return RELATIONS[value] ? value : "";
}

function severityCodeFromBackend(value) {
  const normalized = normalizeForMatch(value || "");
  if (normalized.includes("rat nang")) return "very_severe";
  if (normalized.includes("nang")) return "severe";
  if (normalized.includes("vua")) return "moderate";
  if (normalized.includes("nhe")) return "mild";
  return "";
}

function priorityFromBackend(value) {
  return value && value !== "unknown" ? value : "waiting";
}

function specialtyKeyFromBackend(value) {
  const normalized = normalizeForMatch(value || "");
  if (normalized.includes("tieu hoa")) return "gastro";
  if (normalized.includes("tim mach") || normalized.includes("cap cuu")) return "cardiology";
  if (normalized.includes("tai mui hong")) return "respiratory";
  if (normalized.includes("chan thuong")) return "musculoskeletal";
  if (normalized.includes("tong quat")) return "general";
  return "";
}

function redFlagCodesFromBackend(values = []) {
  const normalizedValues = values.map((value) => normalizeForMatch(value));
  return RED_FLAG_RULES
    .filter((rule) => normalizedValues.some((value) => matchesAny(value, rule.keywords)))
    .map((rule) => rule.code);
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });
  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }
  return response.json();
}

async function ensureBackendSession() {
  if (state.backendSessionId) return;
  const session = await apiRequest("/chat/session", { method: "POST" });
  state.backendSessionId = session.session_id;
  state.backendCaseId = session.case_id;
  state.backendPatientId = session.patient_id;
  state.caseId = session.case_id;
}

async function sendBackendMessage(text) {
  await ensureBackendSession();
  return apiRequest("/chat/message", {
    method: "POST",
    body: JSON.stringify({
      session_id: state.backendSessionId,
      content: text
    })
  });
}

function priorityClass(priority) {
  if (priority === "high") return "queue-badge-alert";
  if (priority === "medium") return "queue-badge-safe";
  return "";
}

function formatDoctorCaseRow(row) {
  const patient = knownOrEmpty(row.patient) || "unknown";
  const age = knownOrEmpty(row.age_or_birth_year) || "unknown";
  const symptom = knownOrEmpty(row.main_symptom) || "Chưa có triệu chứng";
  const specialty = knownOrEmpty(row.suggested_specialty) || "Chưa rõ chuyên khoa";
  const booking = row.booking_status && row.booking_status !== "none"
    ? `${row.booking_status} · ${knownOrEmpty(row.preferred_hospital) || "chưa chọn cơ sở"} · ${knownOrEmpty(row.preferred_time_detail) || "chưa chọn giờ"}`
    : "Chưa có booking";

  return {
    title: `${row.case_id} · ${specialty}`,
    meta: `${patient} · ${age} tuổi · ${symptom}`,
    booking,
    priority: row.priority || "waiting",
    summary: row.doctor_summary || ""
  };
}

function applyDoctorCaseRow(row) {
  state.selectedDoctorCaseId = row.case_id;
  state.caseId = row.case_id;
  state.symptomText = knownOrEmpty(row.main_symptom);
  state.relationCode = relationCodeFromBackend(row.patient);
  state.relationText = knownOrEmpty(row.patient);
  state.age = knownOrEmpty(row.age_or_birth_year);
  state.severityCode = severityCodeFromBackend(row.severity);
  state.severityText = knownOrEmpty(row.severity);
  state.specialtyKey = specialtyKeyFromBackend(row.suggested_specialty);
  state.specialtyText = knownOrEmpty(row.suggested_specialty);
  state.priority = priorityFromBackend(row.priority);
  state.triage = state.priority;
  state.redFlags = redFlagCodesFromBackend(row.red_flags || []);
  state.redFlagText = row.red_flag_status === "confirmed" ? "confirmed" : "";
  state.preferredHospitalText = knownOrEmpty(row.preferred_hospital);
  state.preferredHospitalKey = normalizeHospital(state.preferredHospitalText);
  state.preferredTimeText = knownOrEmpty(row.preferred_time_detail);
  state.preferredTimeKey = normalizeTime(state.preferredTimeText);
  state.bookingStatus = row.booking_status && row.booking_status !== "none" ? row.booking_status : "not_started";
  state.backendDoctorSummary = row.doctor_summary || "";
  state.doctorSummary = state.backendDoctorSummary;
  syncDashboard();
}

function renderDoctorCases() {
  if (!doctorCaseList) return;
  doctorCaseList.innerHTML = "";

  if (!state.doctorCases.length) {
    const empty = document.createElement("p");
    empty.className = "doctor-case-empty";
    empty.textContent = "Chưa có ca AI intake nào. Khi người dùng chat với AI, case sẽ xuất hiện ở đây.";
    doctorCaseList.appendChild(empty);
    return;
  }

  state.doctorCases.forEach((row) => {
    const formatted = formatDoctorCaseRow(row);
    const card = document.createElement("article");
    card.className = "queue-card";

    const badge = document.createElement("span");
    badge.className = `queue-badge ${priorityClass(formatted.priority)}`.trim();
    badge.textContent = formatted.priority.toUpperCase();

    const title = document.createElement("strong");
    title.textContent = formatted.title;

    const meta = document.createElement("p");
    meta.textContent = formatted.meta;

    const booking = document.createElement("p");
    booking.textContent = formatted.booking;

    card.append(badge, title, meta, booking);
    card.addEventListener("click", () => applyDoctorCaseRow(row));
    doctorCaseList.appendChild(card);
  });
}

function renderDoctorStats() {
  const stats = state.doctorStats || {};
  statTotalConversations.textContent = stats.total_conversations ?? 0;
  statRedFlags.textContent = stats.red_flag_cases ?? 0;
  statBookingDrafts.textContent = stats.booking_drafts ?? 0;
}

function withNewCaseReply(replies = []) {
  return [...replies, t("chat.newCase")];
}

async function refreshDoctorCases() {
  if (!state.doctorAuthenticated || !state.backendAvailable) return;
  try {
    state.doctorCases = await apiRequest("/doctor/cases");
    renderDoctorCases();
  } catch (error) {
    console.warn("Could not refresh doctor cases.", error);
  }
}

async function refreshDoctorStats() {
  if (!state.doctorAuthenticated || !state.backendAvailable) return;
  try {
    state.doctorStats = await apiRequest("/doctor/dashboard/stats");
    renderDoctorStats();
  } catch (error) {
    console.warn("Could not refresh doctor stats.", error);
  }
}

function openDoctorLogin() {
  if (state.doctorAuthenticated) {
    showDoctorDashboard();
    return;
  }
  doctorLoginModal.classList.remove("is-hidden");
  doctorLoginModal.setAttribute("aria-hidden", "false");
  doctorNameInput.focus();
}

function closeDoctorLogin() {
  doctorLoginModal.classList.add("is-hidden");
  doctorLoginModal.setAttribute("aria-hidden", "true");
}

async function showDoctorDashboard() {
  dashboardSection.classList.remove("is-hidden");
  dashboardSection.setAttribute("aria-hidden", "false");
  doctorIdentity.textContent = `Đang xem với tài khoản: ${state.doctorName} · ${state.doctorCode}`;
  syncDashboard();
  await refreshDoctorStats();
  await refreshDoctorCases();
  dashboardSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function applyBackendResponse(payload) {
  const caseData = payload.case || {};
  const patient = payload.patient || {};
  const booking = payload.booking || null;

  state.backendAvailable = true;
  state.backendCaseId = caseData.case_id || state.backendCaseId;
  state.backendPatientId = patient.patient_id || state.backendPatientId;
  state.caseId = state.backendCaseId || state.caseId;
  state.symptomText = knownOrEmpty(caseData.main_symptom) || state.symptomText;
  state.relationCode = relationCodeFromBackend(patient.relationship_to_customer);
  state.relationText = knownOrEmpty(patient.relationship_to_customer);
  state.age = knownOrEmpty(patient.age_or_birth_year);
  state.severityCode = severityCodeFromBackend(caseData.severity);
  state.severityText = knownOrEmpty(caseData.severity);
  state.specialtyKey = specialtyKeyFromBackend(caseData.suggested_specialty);
  state.specialtyText = knownOrEmpty(caseData.suggested_specialty);
  state.priority = knownOrEmpty(caseData.priority) || "waiting";
  state.triage = knownOrEmpty(caseData.ai_triage_level) || state.priority;
  state.redFlags = redFlagCodesFromBackend(caseData.red_flags || []);
  state.redFlagText = (caseData.red_flags || []).join(", ");
  state.preferredHospitalText = knownOrEmpty(caseData.preferred_hospital);
  state.preferredHospitalKey = normalizeHospital(state.preferredHospitalText);
  state.preferredTimeText = knownOrEmpty(caseData.preferred_time_detail) || knownOrEmpty(caseData.preferred_time);
  state.preferredTimeKey = normalizeTime(state.preferredTimeText);
  state.backendDoctorSummary = payload.doctor_summary || caseData.doctor_summary || "";
  state.doctorSummary = state.backendDoctorSummary;

  if (booking) {
    state.bookingStatus = booking.booking_status || "draft";
    state.preferredHospitalText = knownOrEmpty(booking.hospital) || state.preferredHospitalText;
    state.preferredHospitalKey = normalizeHospital(state.preferredHospitalText);
    state.preferredTimeText = knownOrEmpty(booking.preferred_time_detail) || knownOrEmpty(booking.preferred_time) || state.preferredTimeText;
    state.preferredTimeKey = normalizeTime(state.preferredTimeText);
  } else if (payload.response_type === "emergency_handoff") {
    state.bookingStatus = "blocked";
  } else if (caseData.booking_id) {
    state.bookingStatus = "draft";
  }

  const responseSteps = {
    ask_more: "backendIntake",
    safe_guidance: "backendGuidance",
    ask_booking_details: "backendBookingDetails",
    booking_confirmation: "backendBookingConfirm",
    booking_created: "bookingComplete",
    emergency_handoff: "emergency"
  };
  state.step = responseSteps[payload.response_type] || "backendIntake";
}

async function handleBackendInput(text) {
  if (!state.backendAvailable) return false;
  try {
    showTyping();
    const payload = await sendBackendMessage(text);
    hideTyping();
    applyBackendResponse(payload);
    addMessage("assistant", payload.assistant_text);
    renderReplies(withNewCaseReply(payload.quick_replies || []));
    syncDashboard();
    await refreshDoctorStats();
    await refreshDoctorCases();
    return true;
  } catch (error) {
    hideTyping();
    state.backendAvailable = false;
    console.warn("Backend unavailable; falling back to frontend mock.", error);
    return false;
  }
}

function getRelationReplyLabels() {
  return ["self", "mother", "father", "child", "other"].map(
    (code) => RELATIONS[code].reply[state.language]
  );
}

function getSeverityReplyLabels() {
  return ["mild", "moderate", "severe", "very_severe"].map((code) => {
    const severity = SEVERITIES[code];
    return severity.reply ? severity.reply[state.language] : severity.label[state.language];
  });
}

function getBookingReplyLabels() {
  return [t("chat.bookVirtual"), t("chat.askMore"), t("chat.monitorMore")];
}

function getHospitalReplyLabels() {
  return ["times_city", "central_park", "da_nang", "not_sure"].map(
    (code) => HOSPITALS[code].label[state.language]
  );
}

function getTimeReplyLabels() {
  return ["tomorrow_morning", "tomorrow_afternoon", "weekend", "choose_later"].map(
    (code) => TIME_WINDOWS[code].label[state.language]
  );
}

function getConfirmReplyLabels() {
  return [t("chat.confirm"), t("chat.editInfo"), t("chat.cancel")];
}

function getWelcomeReplyLabels() {
  return [
    t("chat.welcomeReplySymptoms"),
    t("chat.welcomeReplySpecialty"),
    t("chat.welcomeReplyBooking")
  ];
}

function getRelationLabel(code) {
  return code ? RELATIONS[code].label[state.language] : t("dashboard.notProvided");
}

function getSeverityLabel(code) {
  return code ? SEVERITIES[code].label[state.language] : t("dashboard.notProvided");
}

function getSpecialtyInfoByKey(key) {
  return SPECIALTY_RULES.find((item) => item.key === key) || DEFAULT_SPECIALTY;
}

function getSpecialtyLabel(key) {
  return key ? getSpecialtyInfoByKey(key).label[state.language] : t("dashboard.notProvided");
}

function getHospitalLabel(key, fallback = "") {
  if (key && HOSPITALS[key]) return HOSPITALS[key].label[state.language];
  return fallback || t("dashboard.notProvided");
}

function getTimeLabel(key, fallback = "") {
  if (key && TIME_WINDOWS[key]) return TIME_WINDOWS[key].label[state.language];
  return fallback || t("dashboard.notProvided");
}

function getRedFlagLabels(codes) {
  return codes.map((code) => RED_FLAG_RULES.find((item) => item.code === code)?.label[state.language] || code);
}

function applyStaticTranslations() {
  document.documentElement.lang = state.language;
  document.title = t("page.title");

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder));
  });

  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
  });

  languageButtons.forEach((button) => {
    const isActive = button.dataset.lang === state.language;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
}

function setLanguage(language) {
  if (language !== "vi" && language !== "en") return;
  state.language = language;
  try {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  } catch {
    // no-op
  }

  applyStaticTranslations();
  resetConversation(!chatWidget.classList.contains("is-collapsed"));
}

function addMessage(role, text, options = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  if (options.isHtml) {
    bubble.innerHTML = text;
  } else {
    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    bubble.appendChild(paragraph);
  }

  wrapper.appendChild(bubble);
  messageStream.appendChild(wrapper);
  messageStream.scrollTop = messageStream.scrollHeight;
  state.history.push({ role, text });
}

function showTyping() {
  const wrapper = document.createElement("div");
  wrapper.className = "message assistant";
  wrapper.id = "typingIndicator";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.innerHTML = `
    <div class="typing" aria-label="${t("chatUi.typingAria")}">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `;

  wrapper.appendChild(bubble);
  messageStream.appendChild(wrapper);
  messageStream.scrollTop = messageStream.scrollHeight;
}

function hideTyping() {
  const typing = document.getElementById("typingIndicator");
  if (typing) typing.remove();
}

function respond(text, replies = [], options = {}) {
  showTyping();

  window.setTimeout(() => {
    hideTyping();
    addMessage("assistant", text, options);
    renderReplies(replies);
    syncDashboard();
  }, 520);
}

function renderReplies(replies = []) {
  quickReplies.innerHTML = "";

  const uniqueReplies = [...new Set(replies.filter(Boolean))];
  uniqueReplies.forEach((reply) => {
    const button = document.createElement("button");
    button.className = "quick-reply";
    button.type = "button";
    button.textContent = reply;
    button.addEventListener("click", () => handleUserInput(reply));
    quickReplies.appendChild(button);
  });
}

function detectRedFlags(text) {
  const lowered = normalizeForMatch(text);
  return RED_FLAG_RULES
    .filter((rule) => matchesAny(lowered, rule.keywords))
    .map((rule) => rule.code);
}

function inferSpecialtyInfo(symptomText) {
  const lowered = normalizeForMatch(symptomText);
  return SPECIALTY_RULES.find((item) => matchesAny(lowered, item.keywords)) || DEFAULT_SPECIALTY;
}

function extractAge(text) {
  const match = text.match(/(\d{1,3})/);
  return match ? match[1] : "";
}

function normalizeRelation(text) {
  const lowered = normalizeForMatch(text);

  if (
    lowered === "toi" ||
    lowered === "myself" ||
    lowered === "self" ||
    lowered === "me" ||
    lowered.includes("ban than") ||
    lowered.includes("i am the patient")
  ) {
    return "self";
  }

  if (lowered.includes("me toi") || lowered.includes("my mother") || lowered === "mother") return "mother";
  if (lowered.includes("bo toi") || lowered.includes("cha toi") || lowered.includes("my father") || lowered === "father") return "father";
  if (lowered.includes("con toi") || lowered.includes("my child") || lowered === "child") return "child";
  if (lowered.includes("nguoi than") || lowered.includes("family member") || lowered.includes("relative")) return "other";

  return "";
}

function normalizeSeverity(text) {
  const lowered = normalizeForMatch(text);

  if (lowered.includes("rat nang") || lowered.includes("khong chiu") || lowered.includes("very severe") || lowered.includes("unbearable")) return "very_severe";
  if (lowered.includes("nang") || lowered.includes("severe")) return "severe";
  if (lowered.includes("vua") || lowered.includes("moderate")) return "moderate";
  if (lowered.includes("nhe") || lowered.includes("mild")) return "mild";

  return "";
}

function normalizeHospital(text) {
  const lowered = normalizeForMatch(text);

  for (const [key, hospital] of Object.entries(HOSPITALS)) {
    const viLabel = normalizeForMatch(hospital.label.vi);
    const enLabel = normalizeForMatch(hospital.label.en);
    if (lowered === viLabel || lowered === enLabel || matchesAny(lowered, hospital.keywords)) {
      return key;
    }
  }

  return "";
}

function normalizeTime(text) {
  const lowered = normalizeForMatch(text);

  for (const [key, slot] of Object.entries(TIME_WINDOWS)) {
    const viLabel = normalizeForMatch(slot.label.vi);
    const enLabel = normalizeForMatch(slot.label.en);
    if (lowered === viLabel || lowered === enLabel || matchesAny(lowered, slot.keywords)) {
      return key;
    }
  }

  return "";
}

function isWelcomeIntent(text) {
  const lowered = normalizeForMatch(text);
  return matchesAny(lowered, [
    "khai bao",
    "trieu chung",
    "chuyen khoa",
    "dat lich",
    "symptom",
    "specialty",
    "book",
    "appointment"
  ]);
}

function wantsBooking(text) {
  const lowered = normalizeForMatch(text);
  return matchesAny(lowered, ["dat lich", "book", "booking", "appointment", "virtual visit"]);
}

function wantsAskMore(text) {
  const lowered = normalizeForMatch(text);
  return matchesAny(lowered, ["hoi them", "ask more", "question", "more"]);
}

function wantsConfirm(text) {
  const lowered = normalizeForMatch(text);
  return matchesAny(lowered, ["xac nhan", "confirm"]);
}

function wantsEdit(text) {
  const lowered = normalizeForMatch(text);
  return matchesAny(lowered, ["sua", "edit", "change"]);
}

function wantsNewCase(text) {
  const lowered = normalizeForMatch(text);
  return matchesAny(lowered, ["ca moi", "tao ca moi", "new case", "create a new case"]);
}

function wantsReenterSymptoms(text) {
  const lowered = normalizeForMatch(text);
  return matchesAny(lowered, ["nhap lai", "re-enter", "reenter"]);
}

function buildDoctorSummary() {
  if (state.backendDoctorSummary) {
    state.doctorSummary = state.backendDoctorSummary;
    return;
  }

  if (!state.symptomText) {
    state.doctorSummary = t("dashboard.summaryEmpty");
    return;
  }

  const redFlagText = state.redFlags.length
    ? getRedFlagLabels(state.redFlags).join(", ")
    : t("dashboard.notProvided");
  const bookingSentence = state.bookingStatus === "draft"
    ? format("dashboard.bookingSentenceDraft", {
        hospital: getHospitalLabel(state.preferredHospitalKey, state.preferredHospitalText),
        time: getTimeLabel(state.preferredTimeKey, state.preferredTimeText)
      })
    : t("dashboard.bookingSentenceNone");

  state.doctorSummary = format("dashboard.summaryTemplate", {
    relation: state.relationCode ? getRelationLabel(state.relationCode) : state.relationText || t("dashboard.notProvided"),
    age: state.age || t("dashboard.notProvided"),
    symptom: state.symptomText,
    severity: state.severityCode ? getSeverityLabel(state.severityCode) : state.severityText || t("dashboard.notProvided"),
    redFlags: redFlagText || state.redFlagText,
    specialty: state.specialtyKey ? getSpecialtyLabel(state.specialtyKey) : state.specialtyText || t("dashboard.notProvided"),
    status: state.priority === "high" ? t("dashboard.statusEmergency") : t("dashboard.statusContinue"),
    bookingSentence
  });
}

function syncDashboard() {
  buildDoctorSummary();
  const hasSelectedCase = Boolean(state.symptomText || state.selectedDoctorCaseId || state.backendCaseId);

  caseTitle.textContent = hasSelectedCase ? `Case #${state.caseId}` : t("dashboard.caseNotStarted");
  priorityPill.textContent = state.priority === "waiting" ? t("dashboard.waiting") : state.priority.toUpperCase();
  priorityPill.className = "priority-pill";
  if (state.priority !== "waiting") {
    priorityPill.classList.add(`priority-${state.priority}`);
  }

  symptomValue.textContent = state.symptomText || t("dashboard.notProvided");
  relationValue.textContent = state.relationCode ? getRelationLabel(state.relationCode) : state.relationText || t("dashboard.notProvided");
  ageValue.textContent = state.age || t("dashboard.notProvided");
  severityValue.textContent = state.severityCode ? getSeverityLabel(state.severityCode) : state.severityText || t("dashboard.notProvided");
  specialtyValue.textContent = state.specialtyKey ? getSpecialtyLabel(state.specialtyKey) : state.specialtyText || t("dashboard.notProvided");

  if (state.bookingStatus === "draft") {
    bookingValue.textContent = `${t("dashboard.draftPrefix")} - ${getHospitalLabel(state.preferredHospitalKey, state.preferredHospitalText)} - ${getTimeLabel(state.preferredTimeKey, state.preferredTimeText)}`;
  } else if (state.priority === "high") {
    bookingValue.textContent = t("dashboard.noRegularBooking");
  } else {
    bookingValue.textContent = t("dashboard.notStarted");
  }

  doctorSummary.textContent = state.doctorSummary;

  if (!hasSelectedCase) {
    queueLiveTitle.textContent = t("dashboard.caseNotStarted");
    queueLiveMeta.textContent = t("dashboard.summaryEmpty");
    return;
  }

  queueLiveTitle.textContent = format("dashboard.queueTitleActive", {
    caseId: state.caseId,
    specialty: state.specialtyKey ? getSpecialtyLabel(state.specialtyKey) : state.specialtyText || t("dashboard.intakeInProgress")
  });

  queueLiveMeta.textContent = state.priority === "high"
    ? format("dashboard.queueMetaEmergency", {
        redFlags: getRedFlagLabels(state.redFlags).join(", ") || state.redFlagText || t("dashboard.notProvided")
      })
    : format("dashboard.queueMetaActive", {
        relation: state.relationCode ? getRelationLabel(state.relationCode) : state.relationText || t("dashboard.patientUnknown"),
        severity: state.severityCode ? getSeverityLabel(state.severityCode) : state.severityText || t("dashboard.severityUnknown"),
        bookingStatus: state.bookingStatus === "draft" ? t("dashboard.bookingReady") : t("dashboard.bookingMissing")
      });
}

function askForInitialSymptom() {
  state.step = "collectSymptom";
  respond(t("chat.askInitialSymptom"), []);
}

function startAssessment(text) {
  state.symptomText = text;
  state.redFlags = detectRedFlags(text);

  if (state.redFlags.length) {
    triggerEmergency();
    return;
  }

  const specialty = inferSpecialtyInfo(text);
  state.specialtyKey = specialty.key;
  state.priority = "medium";
  state.triage = "medium";
  state.step = "askRelation";

  respond(t("chat.askRelation"), getRelationReplyLabels());
}

function triggerEmergency() {
  state.priority = "high";
  state.triage = "high";
  state.bookingStatus = "blocked";
  if (!state.specialtyKey) state.specialtyKey = "cardiology";
  state.step = "emergency";

  respond(t("chat.emergency"), [t("chat.understood"), t("chat.reenterSymptoms")]);
}

function finalizeAssessment() {
  const specialty = getSpecialtyInfoByKey(state.specialtyKey);
  const guidanceList = specialty.guidance[state.language].map((item) => `<li>${item}</li>`).join("");
  const warningPreview = specialty.warningSigns[state.language].slice(0, 3).join(", ");

  state.step = "suggestBooking";
  state.priority = "medium";

  respond(
    `
      <p>${t("chat.safeNoEmergency")}</p>
      <ul>${guidanceList}</ul>
      <p>${format("chat.safeSpecialty", {
        specialty: specialty.label[state.language],
        warningSigns: warningPreview
      })}</p>
      <p>${t("chat.safeBookingPrompt")}</p>
    `,
    getBookingReplyLabels(),
    { isHtml: true }
  );
}

function confirmBookingDraft() {
  state.bookingStatus = "draft";
  state.step = "bookingComplete";

  respond(
    format("chat.bookingCreated", {
      specialty: getSpecialtyLabel(state.specialtyKey),
      hospital: getHospitalLabel(state.preferredHospitalKey, state.preferredHospitalText),
      time: getTimeLabel(state.preferredTimeKey, state.preferredTimeText)
    }),
    [t("chat.askMore"), t("chat.newCase")]
  );
}

function resetConversation(keepWidgetOpen = true) {
  state.caseId = generateCaseId();
  state.selectedDoctorCaseId = "";
  state.backendSessionId = "";
  state.backendCaseId = "";
  state.backendPatientId = "";
  state.backendAvailable = true;
  state.step = "welcome";
  state.symptomText = "";
  state.relationCode = "";
  state.relationText = "";
  state.age = "";
  state.severityCode = "";
  state.severityText = "";
  state.specialtyKey = "";
  state.specialtyText = "";
  state.triage = "waiting";
  state.priority = "waiting";
  state.redFlags = [];
  state.redFlagText = "";
  state.bookingIntent = false;
  state.preferredHospitalKey = "";
  state.preferredHospitalText = "";
  state.preferredTimeKey = "";
  state.preferredTimeText = "";
  state.bookingStatus = "not_started";
  state.doctorSummary = "";
  state.backendDoctorSummary = "";
  state.history = [];

  messageStream.innerHTML = "";
  renderReplies(getWelcomeReplyLabels());
  addMessage("assistant", t("chat.welcomeText"));
  syncDashboard();

  if (keepWidgetOpen) {
    chatWidget.classList.remove("is-collapsed");
    chatToggle.style.display = "none";
  } else {
    chatWidget.classList.add("is-collapsed");
    chatToggle.style.display = "block";
  }
}

async function startNewConversation(keepWidgetOpen = true) {
  resetConversation(keepWidgetOpen);
  await refreshDoctorStats();
  await refreshDoctorCases();
}

async function handleUserInput(rawText) {
  const text = rawText.trim();
  if (!text) return;

  addMessage("user", text);
  renderReplies([]);

  if (wantsNewCase(text)) {
    window.setTimeout(() => {
      startNewConversation(true);
    }, 250);
    return;
  }

  if (await handleBackendInput(text)) {
    return;
  }

  if (state.step !== "emergency" && state.step !== "bookingComplete") {
    const freshRedFlags = detectRedFlags(text);
    if (freshRedFlags.length) {
      state.redFlags = freshRedFlags;
      if (!state.symptomText) state.symptomText = text;
      triggerEmergency();
      return;
    }
  }

  switch (state.step) {
    case "welcome":
      if (isWelcomeIntent(text)) {
        askForInitialSymptom();
      } else {
        startAssessment(text);
      }
      break;
    case "collectSymptom":
      startAssessment(text);
      break;
    case "askRelation": {
      const relationCode = normalizeRelation(text);
      if (!relationCode) {
        respond(t("chat.askRelation"), getRelationReplyLabels());
        break;
      }
      state.relationCode = relationCode;
      state.step = "askAge";
      respond(t("chat.askAge"), []);
      break;
    }
    case "askAge": {
      const age = extractAge(text);
      if (!age) {
        respond(t("chat.askAgeRetry"), []);
        break;
      }
      state.age = age;
      state.step = "askSeverity";
      respond(t("chat.askSeverity"), getSeverityReplyLabels());
      break;
    }
    case "askSeverity": {
      const severityCode = normalizeSeverity(text);
      if (!severityCode) {
        respond(t("chat.askSeverityRetry"), getSeverityReplyLabels());
        break;
      }
      state.severityCode = severityCode;
      finalizeAssessment();
      break;
    }
    case "suggestBooking":
      if (wantsBooking(text)) {
        state.bookingIntent = true;
        state.step = "askHospital";
        respond(t("chat.askHospital"), getHospitalReplyLabels());
      } else if (wantsAskMore(text)) {
        respond(t("chat.askMoreContinue"), []);
      } else {
        respond(t("chat.caseSavedMonitor"), getBookingReplyLabels());
      }
      break;
    case "askHospital": {
      state.preferredHospitalKey = normalizeHospital(text);
      state.preferredHospitalText = text;
      state.step = "askTime";
      respond(t("chat.askTime"), getTimeReplyLabels());
      break;
    }
    case "askTime": {
      state.preferredTimeKey = normalizeTime(text);
      state.preferredTimeText = text;
      state.step = "confirmBooking";
      respond(
        format("chat.bookingConfirm", {
          relation: state.relationCode ? getRelationLabel(state.relationCode) : t("dashboard.notProvided"),
          age: state.age || t("dashboard.notProvided"),
          symptom: state.symptomText,
          specialty: getSpecialtyLabel(state.specialtyKey),
          hospital: getHospitalLabel(state.preferredHospitalKey, state.preferredHospitalText),
          time: getTimeLabel(state.preferredTimeKey, state.preferredTimeText)
        }),
        getConfirmReplyLabels()
      );
      break;
    }
    case "confirmBooking":
      if (wantsConfirm(text)) {
        confirmBookingDraft();
      } else if (wantsEdit(text)) {
        state.step = "askHospital";
        respond(t("chat.reaskHospital"), getHospitalReplyLabels());
      } else {
        state.bookingStatus = "cancelled";
        state.step = "suggestBooking";
        respond(t("chat.bookingCancelled"), getBookingReplyLabels());
      }
      break;
    case "emergency":
      if (wantsReenterSymptoms(text)) {
        startNewConversation(true);
      } else {
        respond(t("chat.emergencyFollowup"), [t("chat.newCase")]);
      }
      break;
    case "bookingComplete":
      if (wantsNewCase(text)) {
        startNewConversation(true);
      } else {
        respond(t("chat.bookingHold"), [t("chat.newCase")]);
      }
      break;
    default:
      startNewConversation(true);
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  handleUserInput(chatInput.value);
  chatInput.value = "";
});

chatMinimize.addEventListener("click", () => {
  chatWidget.classList.add("is-collapsed");
  chatToggle.style.display = "block";
});

chatReset.addEventListener("click", () => {
  startNewConversation(true);
});

chatToggle.addEventListener("click", () => {
  chatWidget.classList.remove("is-collapsed");
  chatToggle.style.display = "none";
});

languageButtons.forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.lang));
});

doctorLoginOpen.addEventListener("click", openDoctorLogin);
doctorLoginClose.addEventListener("click", closeDoctorLogin);

doctorLoginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  state.doctorName = doctorNameInput.value.trim();
  state.doctorCode = doctorCodeInput.value.trim();
  if (!state.doctorName || !state.doctorCode) return;

  try {
    const result = await apiRequest("/doctor/login", {
      method: "POST",
      body: JSON.stringify({
        name: state.doctorName,
        code: state.doctorCode
      })
    });
    if (!result.ok) {
      window.alert("Mã bác sĩ không đúng. Dùng mã demo: VINMEC-DR-01");
      return;
    }
    state.doctorName = result.doctor.name;
    state.doctorCode = result.doctor.code;
    state.doctorAuthenticated = true;
    closeDoctorLogin();
    await showDoctorDashboard();
  } catch (error) {
    window.alert("Không kết nối được backend doctor login. Kiểm tra server port 8000.");
    console.warn("Doctor login failed.", error);
  }
});

applyStaticTranslations();
resetConversation(true);
