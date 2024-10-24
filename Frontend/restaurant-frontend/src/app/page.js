import Image from 'next/image';

export default function HomePage() {
  return (
    <div className="bg-gray-100">
      {/* Hero Section */}
      <section
        className="bg-cover bg-center h-screen relative"
        style={{ backgroundImage: "url('/images/restaurant-hero.jpg')" }}
      >
        <div className="absolute inset-0 bg-black opacity-50"></div>
        <div className="container mx-auto flex flex-col items-center justify-center h-full relative z-10 text-white text-center">
          <h1 className="text-5xl font-bold mb-4">Welcome to Our Restaurant</h1>
          <p className="text-xl mb-8">
            Experience the best dining and table booking service
          </p>
          <a
            href="/book-table"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300"
          >
            Book a Table
          </a>
        </div>
      </section>

      {/* About Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-10">
            Table Booking Process
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <Image
                src="/images/placeholder-image.jpg"
                alt="Step 1"
                width={300}
                height={200}
                className="mx-auto mb-4 rounded"
              />
              <h3 className="text-2xl font-semibold mb-2">
                Step 1: Choose Your Date & Time
              </h3>
              <p>Pick a date and time that works best for you to enjoy a delightful meal.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <Image
                src="/images/placeholder-image.jpg"
                alt="Step 2"
                width={300}
                height={200}
                className="mx-auto mb-4 rounded"
              />
              <h3 className="text-2xl font-semibold mb-2">Step 2: Select Your Table</h3>
              <p>Choose from our available tables for the perfect dining experience.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <Image
                src="/images/placeholder-image.jpg"
                alt="Step 3"
                width={300}
                height={200}
                className="mx-auto mb-4 rounded"
              />
              <h3 className="text-2xl font-semibold mb-2">Step 3: Confirm Your Booking</h3>
              <p>Confirm your booking and receive a confirmation email for your reservation.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="bg-gray-200 py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-10">
            What Our Customers Say
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <p className="italic">
                “The booking process was seamless, and the food was incredible!”
              </p>
              <p className="font-bold mt-4">- Jane Doe</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <p className="italic">
                “An amazing experience from start to finish!”
              </p>
              <p className="font-bold mt-4">- John Smith</p>
            </div>
          </div>
        </div>
      </section>

      {/* Add more sections or content to ensure scrolling */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-10">More Information</h2>
          <p className="text-center mb-4">
            Here is some additional content to ensure that the page is scrollable. Add more information about your restaurant, special offers, or any relevant details that your customers might find useful.
          </p>
          {/* Repeat the paragraph or add more content */}
          <p className="text-center mb-4">
            Repeat this paragraph or add additional sections as needed to ensure that the page has enough height to require scrolling.
          </p>
        </div>
      </section>
    </div>
  );
}
