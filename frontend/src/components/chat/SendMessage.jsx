const SendMessage = ({ message }) => {
  return (
    <div className="flex justify-end mb-4">
      <div className="bg-gray-100 text-gray-800 px-4 py-3 rounded-2xl max-w-xs lg:max-w-md">
        {message}
      </div>
    </div>
  );
};

export default SendMessage;
