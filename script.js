// Script to handle interactive elements and animations

document.addEventListener('DOMContentLoaded', () => {

    // 1. Sticky Header Effect
    const header = document.getElementById('main-header');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.add('scrolled'); // Optional: Keep it slightly transparent if desired 
            if(window.scrollY === 0) {
                header.classList.remove('scrolled');
            }
        }
    });

    // 2. Scroll Animation Observer (Micro-animations)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15 // Trigger when 15% of element is visible
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Optional: Stop observing once animated to keep it visible
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Apply observer to elements with animation classes
    const animatedElements = document.querySelectorAll('.fade-in-up, .slide-in-left, .slide-in-right');
    animatedElements.forEach(el => observer.observe(el));

    // 3. Smooth Scroll for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            const targetEl = document.querySelector(targetId);
            
            if(targetEl) {
                window.scrollTo({
                    top: targetEl.offsetTop - 80, // offset for fixed header
                    behavior: 'smooth'
                });
            }
        });
    });

    // 4. Initialize Leaflet Map
    if(document.getElementById('locations-map')) {
        // Set view to center of Vietnam
        const map = L.map('locations-map').setView([14.0583, 108.2772], 5.5);
        
        // Add Dark Theme Map tiles (CartoDB Dark Matter)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> | &copy; <a href="https://carto.com/">CARTO</a>',
            maxZoom: 18,
            subdomains: 'abcd'
        }).addTo(map);

        // Define Locations
        const locations = [
            {
                name: "Phú Quốc",
                coords: [10.2899, 103.9840],
                desc: "Thủ phủ SUP & Foiling. Nước lặng, biển êm, hoàn hảo cho người mới."
            },
            {
                name: "Nha Trang",
                coords: [12.2388, 109.1967],
                desc: "Trạm Lướt Ván (Surfing) lý tưởng với những con sóng đều cả ngày."
            },
            {
                name: "Phú Quý",
                coords: [10.5126, 108.9416],
                desc: "Thánh địa điểm rơi gió (Wind/Kite Surfing) với sức gió cực khủng."
            },
            {
                name: "Bình Châu",
                coords: [10.5367, 107.4947],
                desc: "Trụ sở chính (HQ) & Học viện Thuỷ Tộc. Dịch vụ lưu trú."
            }
        ];

        // Custom marker icon using pure CSS divIcon
        const customIcon = L.divIcon({
            className: 'custom-map-marker',
            html: `<div style="background-color: var(--color-primary); width: 14px; height: 14px; border-radius: 50%; border: 3px solid #fff; box-shadow: 0 0 15px var(--color-primary);"></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });

        // Add markers to map
        locations.forEach(loc => {
            const marker = L.marker(loc.coords, { icon: customIcon }).addTo(map);
            marker.bindPopup(`<h4>📍 ${loc.name}</h4><p>${loc.desc}</p>`);
        });
    }

    // 5. Waitlist Form Submission
    const waitlistForm = document.getElementById('waitlistForm');
    if (waitlistForm) {
        waitlistForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(waitlistForm);
            
            fetch('/submit', {
                method: 'POST',
                body: new URLSearchParams(formData)
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === 'success') {
                    waitlistForm.reset();
                    document.getElementById('formMessage').style.display = 'block';
                    setTimeout(() => {
                        document.getElementById('formMessage').style.display = 'none';
                    }, 5000);
                }
            })
            .catch(error => {
                console.error("Error submitting form", error);
                alert("Có lỗi xảy ra, vui lòng thử lại sau.");
            });
        });
    }

    // 6. Chatbot Widget
    const chatToggle = document.getElementById('chatbot-toggle');
    const chatWindow = document.getElementById('chatbot-window');
    const chatClose = document.getElementById('chatbot-close');
    const chatInput = document.getElementById('chatbot-input');
    const chatSend = document.getElementById('chatbot-send');
    const chatMessages = document.getElementById('chatbot-messages');
    const chatQuick = document.getElementById('chatbot-quick');

    // Sales script knowledge base
    const chatScript = [
        {
            keys: ['khoá học', 'khoa hoc', 'môn', 'dạy gì', 'có gì', 'courses', 'các khoá'],
            answer: 'Hiện tại mình có 3 khoá chính:\n🏄 <b>Surfing</b> — 3 ngày ở Nha Trang, HLV kèm 1-1. Phù hợp mọi trình độ.\n🪁 <b>Kite Surfing</b> — 5 ngày ở Phú Quý, dành cho ai muốn thử thách đỉnh cao.\n🛶 <b>SUP & Efoil</b> — 1 ngày ở Phú Quốc, nhẹ nhàng, cả gia đình chơi được.\nBạn đang quan tâm môn nào?'
        },
        {
            keys: ['giá', 'gia', 'bao nhiêu', 'bao nhieu', 'price', 'chi phí', 'chi phi', 'tiền', 'tien', 'bảng giá'],
            answer: '🏄 Surfing 3 ngày: <b>4.500.000 VNĐ</b> — HLV 1-1, thiết bị, ảnh/video kỷ niệm.\n🪁 Kite Surfing 5 ngày: <b>8.900.000 VNĐ</b> — thiết bị Duotone, chứng nhận IKO.\n🛶 SUP & Efoil 1 ngày: <b>1.200.000 VNĐ</b> — trải nghiệm 2 môn trong 1 ngày.\nTất cả đã bao gồm thiết bị, bảo hiểm, nước uống. Bạn chỉ cần mang đồ bơi thôi!'
        },
        {
            keys: ['an toàn', 'an toan', 'nguy hiểm', 'nguy hiem', 'safety', 'sợ', 'so nuoc', 'sợ nước'],
            answer: 'An toàn là ưu tiên số 1! HLV kèm sát, thiết bị bảo hộ đầy đủ, tập ở vùng nước an toàn. 10 năm hoạt động, chưa có ca tai nạn nghiêm trọng nào.\nNếu bạn sợ nước cũng không sao — 80% học viên ban đầu đều vậy, rồi cuối khoá còn muốn đăng ký thêm! 💪'
        },
        {
            keys: ['đặt lịch', 'dat lich', 'đăng ký', 'dang ky', 'booking', 'book', 'lịch'],
            answer: 'Đơn giản lắm! Bạn có thể:\n1. Nhắn Zalo <b>0339481070</b> để tư vấn & chọn ngày\n2. Hoặc điền form giữ chỗ ngay bên dưới — mình sẽ liên hệ lại trong 24h.\nNên đặt trước 1-2 tuần nhé!',
            cta: true
        },
        {
            keys: ['người mới', 'nguoi moi', 'chưa biết', 'chua biet', 'mới', 'beginner', 'lần đầu', 'lan dau', 'biết gì'],
            answer: 'Được luôn! 80% học viên của mình là người mới hoàn toàn. Khoá Surfing có HLV kèm 1-1, tập từ bờ cát trước rồi mới ra nước. SUP & Efoil thì nhẹ nhàng hơn nữa.\nMình cam kết 100% học viên Surfing đứng được trên ván. Không đứng được thì buổi tiếp miễn phí! 🔥'
        },
        {
            keys: ['nhóm', 'nhom', 'team', 'team building', 'bạn bè', 'ban be', 'group'],
            answer: 'SUP & Efoil ở Phú Quốc là hot nhất cho nhóm — chỉ 1 ngày, ai cũng chơi được, Efoil thì wow factor cực cao!\n👥 Nhóm từ 3 người giảm <b>10%</b>, từ 5 người giảm <b>15%</b>.\nSurfing cũng ok cho team building — nhưng cần 3 ngày nên phù hợp hơn cho trip dài.',
            cta: true
        },
        {
            keys: ['trẻ em', 'tre em', 'con', 'tuổi', 'tuoi', 'kid', 'children', 'gia đình', 'gia dinh', 'family'],
            answer: 'Có nha!\n• SUP & Efoil: từ <b>12 tuổi</b>\n• Surfing: từ <b>10 tuổi</b> (có chương trình riêng)\n• Kite Surfing: từ <b>16 tuổi</b>, cần tối thiểu 45kg\nPhụ huynh có thể tham gia cùng luôn! 👨‍👩‍👧'
        },
        {
            keys: ['mưa', 'mua', 'thời tiết', 'thoi tiet', 'weather', 'sóng', 'song', 'huỷ', 'huy', 'cancel'],
            answer: 'Nếu thời tiết không an toàn, mình sẽ dời lịch miễn phí hoặc hoàn tiền 100%. HLV check điều kiện biển mỗi sáng trước khi quyết định. Bạn không bị mất tiền oan đâu nhé! ☀️'
        },
        {
            keys: ['hlv', 'huấn luyện', 'huan luyen', 'coach', 'instructor', 'giáo viên', 'giao vien', 'chuyên nghiệp'],
            answer: 'Đội ngũ HLV đều có chứng nhận quốc tế (ISA cho Surfing, IKO cho Kite Surfing), kinh nghiệm 10+ năm. Phương pháp dạy dựa trên khoa học — mỗi buổi đều video review để phân tích kỹ thuật cá nhân. 🎓'
        },
        {
            keys: ['đắt', 'dat qua', 'expensive', 'rẻ hơn', 're hon', 'chỗ khác', 'cho khac', 'mắc'],
            answer: 'Mình hiểu! Nhưng thử so sánh nè:\n• Chỗ khác: 5-10 học viên/HLV → ở đây <b>1-1</b>, 100% thời gian cho bạn\n• Giá đã bao gồm tất cả — không phụ thu\n• Cam kết kết quả: không đứng ván được → buổi tiếp miễn phí\nTính ra mỗi ngày chỉ 1.5 triệu cho trải nghiệm premium — rẻ hơn 1 bữa nhậu cuối tuần! 😄'
        },
        {
            keys: ['surfing', 'lướt ván', 'luot van', 'surf'],
            answer: '🏄 <b>Khoá Surfing</b> — 3 ngày ở Nha Trang\n• HLV kèm 1-1, tập từ cơ bản đến cắt sóng\n• Video review mỗi buổi\n• Giá: <b>4.500.000 VNĐ</b> (bao gồm tất cả)\n• Cam kết 100% đứng ván được!\nĐây là khoá bán chạy nhất của mình đó!',
            cta: true
        },
        {
            keys: ['kite', 'diều', 'dieu', 'kitesurfing', 'kitesurf'],
            answer: '🪁 <b>Khoá Kite Surfing</b> — 5 ngày ở Phú Quý\n• HLV certified IKO, tỷ lệ 1:2\n• Thiết bị Duotone cao cấp\n• Giá: <b>8.900.000 VNĐ</b>\n• Phú Quý gió ổn định quanh năm, ít đông đúc\nDành cho ai muốn thử thách đỉnh cao!',
            cta: true
        },
        {
            keys: ['sup', 'efoil', 'e-foil', 'paddle', 'chèo'],
            answer: '🛶 <b>Khoá SUP & Efoil</b> — 1 ngày ở Phú Quốc\n• Sáng: chèo SUP ngắm cảnh biển\n• Chiều: "bay" trên mặt nước với Efoil\n• Giá: <b>1.200.000 VNĐ</b>\n• Phù hợp mọi người, cả gia đình!\nEfoil là công nghệ mới nhất — ít nơi nào ở VN có!',
            cta: true
        },
        {
            keys: ['nghĩ', 'nghi', 'suy nghĩ', 'think', 'chưa sẵn sàng', 'sau', 'later', 'tham khảo'],
            answer: 'Thoải mái! Nếu muốn nhận thông tin chi tiết + ưu đãi sớm nhất thì điền form giữ chỗ nhé — không bắt buộc mua, chỉ để mình gửi thông tin khi có slot mới.',
            cta: true
        },
        {
            keys: ['cảm ơn', 'cam on', 'thanks', 'thank', 'bye', 'tạm biệt'],
            answer: 'Cảm ơn bạn đã ghé Thuỷ Tộc! Nếu sau này muốn tìm hiểu thêm, cứ quay lại chat hoặc nhắn Zalo 0339481070 nhé. Biển luôn ở đó chờ bạn! 🌊'
        }
    ];

    // Quick button mapping
    const quickMap = {
        'courses': 'Thuỷ Tộc có những khoá học gì?',
        'price': 'Giá bao nhiêu?',
        'safety': 'Có an toàn không?',
        'booking': 'Đặt lịch thế nào?'
    };

    function addMessage(text, sender) {
        const msg = document.createElement('div');
        msg.classList.add('chat-msg', sender);
        msg.innerHTML = text;
        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addBotMessage(text, showCta) {
        let html = text.replace(/\n/g, '<br>');
        if (showCta) {
            html += '<br><a href="#contact" class="chat-cta-btn" onclick="document.getElementById(\'chatbot-window\').classList.remove(\'open\')">📋 Điền Form Giữ Chỗ</a>';
        }
        addMessage(html, 'bot');
    }

    function getBotReply(input) {
        const q = input.toLowerCase()
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .replace(/đ/g, 'd').replace(/Đ/g, 'D');

        const inputLower = input.toLowerCase();

        for (const entry of chatScript) {
            for (const key of entry.keys) {
                const keyNorm = key.toLowerCase()
                    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
                    .replace(/đ/g, 'd').replace(/Đ/g, 'D');
                if (q.includes(keyNorm) || inputLower.includes(key)) {
                    return entry;
                }
            }
        }
        return null;
    }

    function handleUserMessage(text) {
        if (!text.trim()) return;
        addMessage(text, 'user');
        chatInput.value = '';

        setTimeout(() => {
            const match = getBotReply(text);
            if (match) {
                addBotMessage(match.answer, match.cta);
            } else {
                addBotMessage('Hmm câu này mình chưa trả lời được 😅 Nhưng bạn nhắn Zalo <b>0339481070</b> là có người tư vấn trực tiếp ngay nhé! Hoặc hỏi mình về <b>khoá học, giá cả, lịch trình</b> — mình sẵn sàng!', false);
            }
        }, 500);
    }

    // Toggle chat window
    if (chatToggle) {
        chatToggle.addEventListener('click', () => {
            chatWindow.classList.toggle('open');
            if (chatWindow.classList.contains('open') && chatMessages.children.length === 0) {
                setTimeout(() => {
                    addBotMessage('Yo! Chào mừng đến với Thuỷ Tộc 🌊<br>Mình là trợ lý tư vấn — hỏi gì về khoá học, giá cả, lịch trình, cứ thoải mái nhé!', false);
                }, 300);
            }
            chatInput.focus();
        });
    }

    if (chatClose) {
        chatClose.addEventListener('click', () => {
            chatWindow.classList.remove('open');
        });
    }

    // Send message
    if (chatSend) {
        chatSend.addEventListener('click', () => handleUserMessage(chatInput.value));
    }
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') handleUserMessage(chatInput.value);
        });
    }

    // Quick buttons
    if (chatQuick) {
        chatQuick.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const q = btn.getAttribute('data-q');
                handleUserMessage(quickMap[q] || btn.textContent);
            });
        });
    }

});
